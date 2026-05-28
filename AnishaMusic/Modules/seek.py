# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

from AnishaMusic import BOT_USERNAME, app, anishadb, pytgcalls
from AnishaMusic.Helpers import admin_check, buttons
from AnishaMusic.Helpers.bass_db import get_bass_seek_params
import os

@app.on_message(filters.command(["seek", "cseek", "seekback", "cseekback"]) & filters.group)
@admin_check
async def seek_cmd(_, message: Message):
    from AnishaMusic.Helpers.active import currently_playing
    chat_id = message.chat.id
    curr = currently_playing.get(chat_id)
    if not curr:
        return await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴘʟᴀʏɪɴɢ ʀɪɢʜᴛ ɴᴏᴡ!")

    try:
        duration = curr.get("duration")
        if not duration or duration == "0:00":
            return await message.reply_text("» ᴄᴀɴ'ᴛ sᴇᴇᴋ ᴛʜɪs ᴛʀᴀᴄᴋ!")
            
        seek_to = message.command[1]
        
        # Parse minutes:seconds or just seconds
        if ":" in seek_to:
            mins, secs = seek_to.split(":")
            seek_secs = int(mins) * 60 + int(secs)
        else:
            seek_secs = int(seek_to)
            
    except (IndexError, ValueError):
        return await message.reply_text("» ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴛɪᴍᴇ ᴛᴏ sᴇᴇᴋ.\nᴇxᴀᴍᴘʟᴇ: `/seek 30` ᴏʀ `/seek 1:30`")

    title = curr["title"]
    file_path = curr["file_path"]
    stream_type = curr.get("stream_type", "audio")

    if not os.path.exists(file_path):
        return await message.reply_text("» ᴛʀᴀᴄᴋ ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ, ᴄᴀɴɴᴏᴛ sᴇᴇᴋ.")

    ffmpeg_params = get_bass_seek_params(chat_id, seek_secs)

    try:
        if stream_type == "video":
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=ffmpeg_params)
        else:
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_params)
        
        await pytgcalls.play(chat_id, stream)
        await message.reply_text(f"⏩ **sᴇᴇᴋᴇᴅ ᴛᴏ {seek_secs}s**\n\n» **ᴛʀᴀᴄᴋ:** {title}")
    except Exception as e:
        await message.reply_text(f"» ᴇʀʀᴏʀ sᴇᴇᴋɪɴɢ: `{e}`")
