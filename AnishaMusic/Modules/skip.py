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
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

from AnishaMusic import BOT_USERNAME, LOGGER, app, anishadb, pytgcalls
from AnishaMusic.Helpers.bass_db import get_bass_params
from AnishaMusic.Helpers import _clear_, admin_check, buttons, close_key, gen_thumb
from AnishaMusic.Helpers.logger import log_activity
from AnishaMusic.Helpers.error_reporter import report_error
import asyncio
import os


@app.on_message(filters.command(["skip", "next"]) & filters.group)
@admin_check
async def skip_str(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    get = anishadb.get(message.chat.id)
    if not get:
        try:
            await _clear_(message.chat.id)
            await pytgcalls.leave_call(message.chat.id)
            await message.reply_text(
                text=f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🥺\n│ \n└ʙʏ : {message.from_user.mention} 🥀\n\n**» ɴᴏ ᴍᴏʀᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ɪɴ** {message.chat.title}, **ʟᴇᴀᴠɪɴɢ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
                reply_markup=close_key,
            )
            await log_activity(
                "SKIP",
                "Skipped last track, queue empty — left voice chat.",
                chat_id=message.chat.id,
                chat_title=message.chat.title,
                user=message.from_user.first_name,
            )
        except:
            return
    else:
        title = get[0]["title"]
        duration = get[0]["duration"]
        file_path = get[0]["file_path"]
        videoid = get[0]["videoid"]
        req_by = get[0]["req"]
        user_id = get[0]["user_id"]
        stream_type = get[0].get("stream_type", "audio")
        get.pop(0)

        if not os.path.exists(file_path):
            from AnishaMusic.Helpers.downloaders import resolve_and_download
            file_path, videoid = await resolve_and_download(title, videoid, stream_type)
            if not file_path or not os.path.exists(file_path):
                await _clear_(message.chat.id)
                return await pytgcalls.leave_call(message.chat.id)


        if stream_type == "video":
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=get_bass_params(message.chat.id))
        else:
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=get_bass_params(message.chat.id))
        try:
            await pytgcalls.play(
                message.chat.id,
                stream,
            )
        except Exception as e:
            LOGGER.error(f"Error in skip: {e}")
            await report_error(
                module="skip",
                error=e,
                chat_id=message.chat.id,
                chat_title=message.chat.title,
                user=message.from_user.first_name if message.from_user else "Unknown",
            )
            await _clear_(message.chat.id)
            return await pytgcalls.leave_call(message.chat.id)

        from AnishaMusic.Helpers.active import currently_playing
        currently_playing[message.chat.id] = {
            "title": title,
            "duration": duration,
            "file_path": file_path,
            "videoid": videoid,
            "req": req_by,
            "user_id": user_id,
            "stream_type": stream_type,
        }
        from AnishaMusic.Helpers.queue import preload_next_track
        asyncio.create_task(preload_next_track(message.chat.id))

        await message.reply_text(
            text=f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🥺\n│ \n└ʙʏ : {message.from_user.mention} 🥀",
            reply_markup=close_key,
        )
        await log_activity(
            "SKIP",
            f"Skipped to: **{title}** (`{duration}`)",
            chat_id=message.chat.id,
            chat_title=message.chat.title,
            user=message.from_user.first_name,
        )
        async def send_skip_msg():
            img = await gen_thumb(videoid, user_id)
            await message.reply_photo(
                photo=img,
                caption=f"**➻ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ**\n\n‣ **ᴛɪᴛʟᴇ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}` ᴍɪɴᴜᴛᴇs\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {req_by}",
                reply_markup=buttons,
            )
        asyncio.create_task(send_skip_msg())
        return
