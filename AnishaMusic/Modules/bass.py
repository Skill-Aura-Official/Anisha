# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

from AnishaMusic import BOT_USERNAME, app, anishadb, pytgcalls
from AnishaMusic.Helpers import admin_check, buttons
from AnishaMusic.Helpers.bass_db import set_bass, get_bass_params
from AnishaMusic.Helpers.logger import log_activity

@app.on_message(filters.command(["bass"]) & filters.group)
@admin_check
async def bass_cmd(_, message: Message):
    from AnishaMusic.Helpers.active import currently_playing
    chat_id = message.chat.id
    curr = currently_playing.get(chat_id)
    if not curr:
        return await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴘʟᴀʏɪɴɢ ʀɪɢʜᴛ ɴᴏᴡ!")

    try:
        level = int(message.command[1])
        if level < 0 or level > 100:
            return await message.reply_text("» ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ʙᴀss ʟᴇᴠᴇʟ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ 100.\nᴇxᴀᴍᴘʟᴇ: `/bass 35`")
    except (IndexError, ValueError):
        return await message.reply_text("» ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ʙᴀss ʟᴇᴠᴇʟ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ 100.\nᴇxᴀᴍᴘʟᴇ: `/bass 35`")

    title = curr["title"]
    file_path = curr["file_path"]
    stream_type = curr.get("stream_type", "audio")

    set_bass(chat_id, level)
    ffmpeg_params = get_bass_params(chat_id)

    try:
        if stream_type == "video":
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=ffmpeg_params)
        else:
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_params)

        await pytgcalls.play(chat_id, stream)
        await message.reply_text(f"🎸 **ʙᴀss ʙᴏᴏsᴛ ᴀᴘᴘʟɪᴇᴅ**\n\n» ʙᴀss ʟᴇᴠᴇʟ sᴇᴛ ᴛᴏ: `{level}`\n» **ᴛʀᴀᴄᴋ:** {title}")
        await log_activity(
            "BASS",
            f"Bass set to `{level}` on: **{title}**",
            chat_id=chat_id,
            chat_title=message.chat.title,
            user=message.from_user.first_name,
        )
    except Exception as e:
        await message.reply_text(f"» ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ʙᴀss: `{e}`")
