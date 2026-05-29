# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, Update, ChatUpdate
from pytgcalls import filters as ptgfilters

from AnishaMusic import BOT_ID, BOT_USERNAME, app, app2, anishadb, pytgcalls, LOGGER
from AnishaMusic.Helpers.bass_db import get_bass_params
from AnishaMusic.Helpers.thumbnails import gen_qthumb, gen_thumb
from AnishaMusic.Helpers import _clear_, buttons, gen_thumb
from AnishaMusic.Helpers.logger import log_activity
from AnishaMusic.Helpers.error_reporter import report_error
import asyncio
import os
import traceback

welcome = 20
close = 30

MAX_AUTO_SKIP_RETRIES = 5


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    try:
        await _clear_(message.chat.id)
        await pytgcalls.leave_call(message.chat.id)
    except:
        pass


@app.on_message(filters.left_chat_member)
async def ub_leave(_, message: Message):
    if message.left_chat_member.id == BOT_ID:
        try:
            await _clear_(message.chat.id)
            await pytgcalls.leave_call(message.chat.id)
        except:
            pass
        try:
            await app2.leave_chat(message.chat.id)
        except:
            pass


@app.on_message(filters.new_chat_members)
async def newly_joined(_, message: Message):
    if any(member.id == BOT_ID for member in message.new_chat_members):
        chat = message.chat
        user = message.from_user.first_name if message.from_user else "Unknown User"
        await log_activity(
            "JOINED_GROUP",
            f"Bot was added to group: **{chat.title}**\nAdded by: **{user}**",
            chat_id=chat.id,
            chat_title=chat.title,
            user=user,
        )


@pytgcalls.on_update(ptgfilters.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP | ChatUpdate.Status.CLOSED_VOICE_CHAT))
async def swr_handler(_, update: Update):
    chat_id = update.chat_id
    try:
        await _clear_(chat_id)
    except:
        pass


from pytgcalls.types import StreamEnded

@pytgcalls.on_update(ptgfilters.stream_end(stream_type=StreamEnded.Type.AUDIO))
async def on_stream_end(pytgcalls, update: Update):
    chat_id = update.chat_id

    # Use a loop with max retries instead of recursion to prevent stack overflow
    for attempt in range(MAX_AUTO_SKIP_RETRIES):
        get = anishadb.get(chat_id)
        if not get:
            try:
                await _clear_(chat_id)
                await pytgcalls.leave_call(chat_id)
                await log_activity(
                    "AUTO_NEXT",
                    "Queue empty — left voice chat.",
                    chat_id=chat_id,
                )
            except:
                pass
            return

        process = None
        try:
            process = await app.send_message(
                chat_id=chat_id,
                text="» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɴᴇxᴛ ᴛʀᴀᴄᴋ ғʀᴏᴍ ǫᴜᴇᴜᴇ...",
            )
            title = get[0]["title"]
            duration = get[0]["duration"]
            file_path = get[0]["file_path"]
            videoid = get[0]["videoid"]
            req_by = get[0]["req"]
            user_id = get[0]["user_id"]
            stream_type = get[0].get("stream_type", "audio")
            get.pop(0)

            if not os.path.exists(file_path):
                from AnishaMusic.Helpers.saavn import saavn_download
                try:
                    file_path = await saavn_download(title)
                    videoid = videoid
                except Exception:
                    from AnishaMusic.Helpers.downloaders import resolve_and_download
                    file_path, videoid = await resolve_and_download(title, videoid, stream_type)
                if not file_path or not os.path.exists(file_path):
                    try:
                        await process.edit_text("» sᴋɪᴘᴘɪɴɢ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ ᴅᴜᴇ ᴛᴏ ʀᴇsᴏʟᴜᴛɪᴏɴ ᴇʀʀᴏʀ...")
                    except:
                        pass
                    continue  # Retry with next track in queue

            if stream_type == "video":
                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=get_bass_params(chat_id))
            else:
                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=get_bass_params(chat_id))

            try:
                await pytgcalls.play(
                    chat_id,
                    stream,
                )
            except Exception:
                await _clear_(chat_id)
                await pytgcalls.leave_call(chat_id)
                return

            from AnishaMusic.Helpers.active import currently_playing
            currently_playing[chat_id] = {
                "title": title,
                "duration": duration,
                "file_path": file_path,
                "videoid": videoid,
                "req": req_by,
                "user_id": user_id,
                "stream_type": stream_type,
            }
            from AnishaMusic.Helpers.queue import preload_next_track
            asyncio.create_task(preload_next_track(chat_id))

            await log_activity(
                "AUTO_NEXT",
                f"Auto-playing next: **{title}** (`{duration}`)",
                chat_id=chat_id,
            )

            async def send_auto_msg():
                img = await gen_thumb(videoid, user_id)
                try:
                    await process.delete()
                except:
                    pass
                await app.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption=f"**➻ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ**\n\n‣ **ᴛɪᴛʟᴇ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}` ᴍɪɴᴜᴛᴇs\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {req_by}",
                    reply_markup=buttons,
                )
            asyncio.create_task(send_auto_msg())
            return  # Success — exit the retry loop

        except Exception as e:
            LOGGER.error(f"Watcher Error (attempt {attempt + 1}): {e}\n{traceback.format_exc()}")
            await report_error(
                module="watcher/stream_end",
                error=e,
                chat_id=chat_id,
                extra_info=f"Auto-skip attempt {attempt + 1}/{MAX_AUTO_SKIP_RETRIES}",
            )
            try:
                if process:
                    await process.edit_text("» sᴋɪᴘᴘɪɴɢ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ ᴅᴜᴇ ᴛᴏ ᴇʀʀᴏʀ...")
            except:
                pass
            continue  # Retry with next track

    # All retries exhausted
    LOGGER.error(f"Watcher: Exhausted {MAX_AUTO_SKIP_RETRIES} retries for chat {chat_id}, clearing.")
    try:
        await _clear_(chat_id)
        await pytgcalls.leave_call(chat_id)
    except:
        pass
