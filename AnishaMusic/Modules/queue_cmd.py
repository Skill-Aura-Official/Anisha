import os
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AnishaMusic import BOT_USERNAME, app, anishadb
from AnishaMusic.Helpers import get_readable_time

@app.on_message(filters.command(["queue", "q"]) & filters.group)
async def queue_cmd(_, message: Message):
    chat_id = message.chat.id
    get = anishadb.get(chat_id)
    if not get:
        return await message.reply_text("» **ᴏ̨ᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ** 🥺")

    msg = f"**➻ ᴏ̨ᴜᴇᴜᴇ ʟɪsᴛ ғᴏʀ {message.chat.title}**\n\n"
    
    # Current playing
    current = get[0]
    msg += f"**[0]** **ᴄᴜʀʀᴇɴᴛʟʏ ᴘʟᴀʏɪɴɢ:**\n"
    msg += f"‣ [{current['title'][:30]}](https://t.me/{BOT_USERNAME}?start=info_{current['videoid']})\n"
    msg += f"‣ **ᴛʏᴘᴇ:** `{current.get('stream_type', 'audio').capitalize()}`\n"
    msg += f"‣ **ᴅᴜʀᴀᴛɪᴏɴ:** `{current['duration']}` ᴍɪɴᴜᴛᴇs\n"
    msg += f"‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {current['req']}\n\n"

    # Queued tracks
    if len(get) > 1:
        msg += "**➻ ᴜᴘᴄᴏᴍɪɴɢ ᴛʀᴀᴄᴋs:**\n\n"
        for i, track in enumerate(get[1:], start=1):
            title = track['title'][:25]
            stream_type = track.get('stream_type', 'audio').capitalize()
            duration = track['duration']
            req = track['req']
            msg += f"**[{i}]** [{title}...](https://t.me/{BOT_USERNAME}?start=info_{track['videoid']}) | `{stream_type}` | `{duration}` | `{req}`\n"

            
            if i >= 10:
                msg += f"\n**... ᴀɴᴅ {len(get) - 11} ᴍᴏʀᴇ ᴛʀᴀᴄᴋs.**\n"
                break

    close_mark = InlineKeyboardMarkup([[InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="close")]])
    await message.reply_text(msg, disable_web_page_preview=True, reply_markup=close_mark)
