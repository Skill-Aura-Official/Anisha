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
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
import asyncio
import os

from AnishaMusic import (
    ASS_ID,
    ASS_NAME,
    BOT_ID,
    BOT_MENTION,
    BOT_USERNAME,
    LOGGER,
    app,
    anishadb,
    pytgcalls,
)
from AnishaMusic.Helpers import (
    _clear_,
    admin_check_cb,
    gen_thumb,
    is_streaming,
    stream_off,
    stream_on,
)
from AnishaMusic.Helpers.dossier import *
from AnishaMusic.Helpers.inline import (
    buttons,
    close_key,
    help_back,
    helpmenu,
    pm_buttons,
)
from AnishaMusic.Helpers.logger import log_activity
from AnishaMusic.Helpers.error_reporter import report_error


@app.on_callback_query(filters.regex("forceclose"))
async def close_(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(
                "» ɪᴛ'ʟʟ ʙᴇ ʙᴇᴛᴛᴇʀ ɪғ ʏᴏᴜ sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs ʙᴀʙʏ.", show_alert=True
            )
        except:
            return
    await CallbackQuery.message.delete()
    try:
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(filters.regex("close"))
async def forceclose_command(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
    except:
        return
    try:
        await CallbackQuery.answer()
    except:
        pass


@app.on_callback_query(filters.regex(pattern=r"^(resume_cb|pause_cb|skip_cb|end_cb)$"))
@admin_check_cb
async def admin_cbs(_, query: CallbackQuery):
    try:
        await query.answer()
    except:
        pass

    data = query.matches[0].group(1)

    if data == "resume_cb":
        if await is_streaming(query.message.chat.id):
            return await query.answer(
                "ᴅɪᴅ ʏᴏᴜ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ʏᴏᴜ ᴘᴀᴜsᴇᴅ ᴛʜᴇ sᴛʀᴇᴀᴍ ?", show_alert=True
            )
        await stream_on(query.message.chat.id)
        await pytgcalls.resume(query.message.chat.id)
        await query.message.reply_text(
            text=f"➻ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ 💫\n│ \n└ʙʏ : {query.from_user.mention} 🥀",
            reply_markup=close_key,
        )
        await log_activity(
            "RESUME",
            "Stream resumed.",
            chat_id=query.message.chat.id,
            chat_title=query.message.chat.title,
            user=query.from_user.first_name,
        )

    elif data == "pause_cb":
        if not await is_streaming(query.message.chat.id):
            return await query.answer(
                "ᴅɪᴅ ʏᴏᴜ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ʏᴏᴜ ʀᴇsᴜᴍᴇᴅ ᴛʜᴇ sᴛʀᴇᴀᴍ ?", show_alert=True
            )
        await stream_off(query.message.chat.id)
        await pytgcalls.pause(query.message.chat.id)
        await query.message.reply_text(
            text=f"➻ sᴛʀᴇᴀᴍ ᴩᴀᴜsᴇᴅ 🥺\n│ \n└ʙʏ : {query.from_user.mention} 🥀",
            reply_markup=close_key,
        )
        await log_activity(
            "PAUSE",
            "Stream paused.",
            chat_id=query.message.chat.id,
            chat_title=query.message.chat.title,
            user=query.from_user.first_name,
        )

    elif data == "end_cb":
        try:
            await _clear_(query.message.chat.id)
            await pytgcalls.leave_call(query.message.chat.id)
        except:
            pass
        await query.message.reply_text(
            text=f"➻ sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ/sᴛᴏᴩᴩᴇᴅ ❄\n│ \n└ʙʏ : {query.from_user.mention} 🥀",
            reply_markup=close_key,
        )
        await query.message.delete()
        await log_activity(
            "STOP",
            "Stream ended via inline button.",
            chat_id=query.message.chat.id,
            chat_title=query.message.chat.title,
            user=query.from_user.first_name,
        )

    elif data == "skip_cb":
        get = anishadb.get(query.message.chat.id)
        if not get:
            try:
                await _clear_(query.message.chat.id)
                await pytgcalls.leave_call(query.message.chat.id)
                await query.message.reply_text(
                    text=f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🥺\n│ \n└ʙʏ : {query.from_user.mention} 🥀\n\n**» ɴᴏ ᴍᴏʀᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ɪɴ** {query.message.chat.title}, **ʟᴇᴀᴠɪɴɢ ᴠɪᴅᴇᴏᴄʜᴀᴛ.**",
                    reply_markup=close_key,
                )
                await log_activity(
                    "SKIP",
                    "Skipped last track (inline), queue empty — left voice chat.",
                    chat_id=query.message.chat.id,
                    chat_title=query.message.chat.title,
                    user=query.from_user.first_name,
                )
                return await query.message.delete()
            except:
                return
        else:
            title = get[0]["title"]
            duration = get[0]["duration"]
            videoid = get[0]["videoid"]
            file_path = get[0]["file_path"]
            req_by = get[0]["req"]
            user_id = get[0]["user_id"]
            stream_type = get[0].get("stream_type", "audio")
            get.pop(0)

            if not os.path.exists(file_path):
                from AnishaMusic.Helpers.downloaders import resolve_and_download
                file_path, videoid = await resolve_and_download(title, videoid, stream_type)
                if not file_path or not os.path.exists(file_path):
                    await _clear_(query.message.chat.id)
                    return await pytgcalls.leave_call(query.message.chat.id)


            from AnishaMusic.Helpers.bass_db import get_bass_params
            ffmpeg_params = get_bass_params(query.message.chat.id)

            if stream_type == "video":
                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=ffmpeg_params)
            else:
                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_params)

            try:
                await pytgcalls.play(
                    query.message.chat.id,
                    stream,
                )
            except Exception as ex:
                LOGGER.error(ex)
                await report_error(
                    module="callback/skip_cb",
                    error=ex,
                    chat_id=query.message.chat.id,
                    chat_title=query.message.chat.title,
                    user=query.from_user.first_name,
                    extra_info=f"Failed to play next track: {title[:50]}",
                )
                await _clear_(query.message.chat.id)
                return await pytgcalls.leave_call(query.message.chat.id)

            from AnishaMusic.Helpers.active import currently_playing
            currently_playing[query.message.chat.id] = {
                "title": title,
                "duration": duration,
                "file_path": file_path,
                "videoid": videoid,
                "req": req_by,
                "user_id": user_id,
                "stream_type": stream_type,
            }
            from AnishaMusic.Helpers.queue import preload_next_track
            asyncio.create_task(preload_next_track(query.message.chat.id))

            img = await gen_thumb(videoid, user_id)
            await query.edit_message_text(
                text=f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🥺\n│ \n└ʙʏ : {query.from_user.mention} 🥀",
                reply_markup=close_key,
            )
            await log_activity(
                "SKIP",
                f"Skipped to (inline): **{title}** (`{duration}`)",
                chat_id=query.message.chat.id,
                chat_title=query.message.chat.title,
                user=query.from_user.first_name,
            )
            return await query.message.reply_photo(
                photo=img,
                caption=f"**➻ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ**\n\n‣ **ᴛɪᴛʟᴇ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}` ᴍɪɴᴜᴛᴇs\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {req_by}",
                reply_markup=buttons,
            )


@app.on_callback_query(filters.regex("unban_ass"))
async def unban_ass(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id, user_id = callback_request.split("|")
    umm = (await app.get_chat_member(int(chat_id), BOT_ID)).privileges
    if umm.can_restrict_members:
        try:
            await app.unban_chat_member(int(chat_id), ASS_ID)
        except:
            return await CallbackQuery.answer(
                "» ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ ᴀssɪsᴛᴀɴᴛ.",
                show_alert=True,
            )
        return await CallbackQuery.edit_message_text(
            f"➻ {ASS_NAME} sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ ʙʏ {CallbackQuery.from_user.mention}.\n\nᴛʀʏ ᴘʟᴀʏɪɴɢ ɴᴏᴡ..."
        )
    else:
        return await CallbackQuery.answer(
            "» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴜɴʙᴀɴ ᴜsᴇʀs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.",
            show_alert=True,
        )


@app.on_callback_query(filters.regex("anisha_help"))
async def help_menu(_, query: CallbackQuery):
    try:
        await query.answer()
    except:
        pass

    try:
        await query.edit_message_text(
            text=f"๏ ʜᴇʏ {query.from_user.first_name}, 🥀\n\nᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴɴᴀ ɢᴇᴛ ʜᴇʟᴘ.",
            reply_markup=InlineKeyboardMarkup(helpmenu),
        )
    except Exception as e:
        LOGGER.error(e)
        return


@app.on_callback_query(filters.regex("anisha_cb"))
async def open_hmenu(_, query: CallbackQuery):
    callback_data = query.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = InlineKeyboardMarkup(help_back)

    try:
        await query.answer()
    except:
        pass

    if cb == "help":
        text = HELP_TEXT
    elif cb == "sudo":
        text = HELP_SUDO
    elif cb == "owner":
        text = HELP_DEV
    else:
        return

    if query.message.photo:
        await query.message.delete()
        await query.message.reply_text(text, reply_markup=keyboard)
    else:
        await query.edit_message_text(text, reply_markup=keyboard)


@app.on_callback_query(filters.regex("anisha_home"))
async def home_anisha(_, query: CallbackQuery):
    try:
        await query.answer()
    except:
        pass
    try:
        text = PM_START_TEXT.format(
            query.from_user.first_name,
            BOT_MENTION,
        )
        markup = InlineKeyboardMarkup(pm_buttons)

        if not query.message.photo:
            import config
            await query.message.delete()
            await query.message.reply_photo(
                photo=config.START_IMG,
                caption=text,
                reply_markup=markup,
            )
        else:
            await query.edit_message_text(
                text=text,
                reply_markup=markup,
            )
    except:
        pass
