# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

from AnishaMusic import app, pytgcalls
from AnishaMusic.Helpers import admin_check
from AnishaMusic.Helpers.bass_db import chat_preset_db, get_bass_params
from AnishaMusic.Helpers.active import currently_playing
from AnishaMusic.Helpers.logger import log_activity

PRESET_LABELS = {
    "bass": "🎸 Bass Boost (Default)",
    "jazz": "🎷 Jazz (Smooth & Warm)",
    "clean": "🎧 Clean/Flat (High Fidelity)",
    "vocal": "🎤 Vocal/Acoustic (Clear)",
    "heavy": "💥 Heavy Bass (Club style)"
}

@app.on_message(filters.command(["preset", "presets", "equalizer", "eq"]) & filters.group)
@admin_check
async def set_preset_cmd(_, message: Message):
    chat_id = message.chat.id

    # If a specific preset name is provided in the command args
    if len(message.command) > 1:
        preset_name = message.command[1].lower()
        if preset_name not in PRESET_LABELS:
            valid_list = ", ".join(f"`{k}`" for k in PRESET_LABELS.keys())
            return await message.reply_text(f"» ɪɴᴠᴀʟɪᴅ ᴘʀᴇsᴇᴛ! ᴄʜᴏᴏsᴇ ғʀᴏᴍ: {valid_list}")

        chat_preset_db[chat_id] = preset_name

        # Apply to currently playing stream if active
        curr = currently_playing.get(chat_id)
        if curr:
            file_path = curr["file_path"]
            stream_type = curr.get("stream_type", "audio")
            ffmpeg_params = get_bass_params(chat_id)

            if stream_type == "video":
                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=ffmpeg_params)
            else:
                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_params)

            try:
                await pytgcalls.play(chat_id, stream)
            except Exception as e:
                return await message.reply_text(f"» ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ᴘʀᴇsᴇᴛ: `{e}`")

        await log_activity(
            "PRESET",
            f"Preset set to: **{PRESET_LABELS[preset_name]}**",
            chat_id=chat_id,
            chat_title=message.chat.title,
            user=message.from_user.first_name,
        )
        return await message.reply_text(f"✨ **ᴘʀᴇsᴇᴛ ᴀᴘᴘʟɪᴇᴅ**\n\n» **ᴘʀᴇsᴇᴛ:** {PRESET_LABELS[preset_name]}")

    # Show inline menu
    current_preset = chat_preset_db.get(chat_id, "bass")
    buttons = []
    for k, v in PRESET_LABELS.items():
        label = f"✅ {v}" if k == current_preset else v
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"set_preset {k}|{message.from_user.id}")])

    markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        "🎚 **ᴀɴɪsʜᴀ ᴍᴜsɪᴄ ᴘʀᴇsᴇᴛs**\n\nᴄʜᴏᴏsᴇ ᴀ ᴘʀᴇsᴇᴛ ᴛᴏ ɪɴsᴛᴀɴᴛʟʏ ᴛᴜɴᴇ ᴛʜᴇ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ:",
        reply_markup=markup
    )


@app.on_callback_query(filters.regex(r"^set_preset "))
async def set_preset_cb(_, query):
    chat_id = query.message.chat.id
    data = query.data.split(None, 1)[1]
    preset_name, user_id = data.split("|")

    if query.from_user.id != int(user_id):
        return await query.answer("» ɪᴛ'ʟʟ ʙᴇ ʙᴇᴛᴛᴇʀ ɪғ ʏᴏᴜ sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs ʙᴀʙʏ.", show_alert=True)

    if preset_name not in PRESET_LABELS:
        return await query.answer("» Invalid preset.", show_alert=True)

    chat_preset_db[chat_id] = preset_name
    await query.answer(f"Preset set to: {preset_name.upper()}")

    # Re-render keyboard with the new active preset marked
    buttons = []
    for k, v in PRESET_LABELS.items():
        label = f"✅ {v}" if k == preset_name else v
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"set_preset {k}|{user_id}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass

    # Apply to currently playing stream if active
    curr = currently_playing.get(chat_id)
    if curr:
        file_path = curr["file_path"]
        stream_type = curr.get("stream_type", "audio")
        ffmpeg_params = get_bass_params(chat_id)

        if stream_type == "video":
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=ffmpeg_params)
        else:
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ffmpeg_params)

        try:
            await pytgcalls.play(chat_id, stream)
            await query.message.reply_text(f"✨ **ᴘʀᴇsᴇᴛ ᴀᴘᴘʟɪᴇᴅ**\n\n» **ᴘʀᴇsᴇᴛ:** {PRESET_LABELS[preset_name]}\n» **ᴛʀᴀᴄᴋ:** {curr['title']}")
        except Exception as e:
            await query.message.reply_text(f"» ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ᴘʀᴇsᴇᴛ: `{e}`")

    await log_activity(
        "PRESET",
        f"Preset set to: **{PRESET_LABELS[preset_name]}** (inline)",
        chat_id=chat_id,
        chat_title=query.message.chat.title,
        user=query.from_user.first_name,
    )
