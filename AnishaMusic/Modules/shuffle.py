# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

from pyrogram import filters
from pyrogram.types import Message
import random

from AnishaMusic import app, anishadb
from AnishaMusic.Helpers import admin_check

@app.on_message(filters.command(["shuffle", "cshuffle"]) & filters.group)
@admin_check
async def shuffle_cmd(_, message: Message):
    chat_id = message.chat.id
    get = anishadb.get(chat_id)
    
    if not get:
        return await message.reply_text("» ɴᴏᴛʜɪɴɢ ɪs ᴘʟᴀʏɪɴɢ ʀɪɢʜᴛ ɴᴏᴡ!")
        
    if len(get) < 3:
        return await message.reply_text("» ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴛʀᴀᴄᴋs ɪɴ ᴏ̨ᴜᴇᴜᴇ ᴛᴏ sʜᴜғғʟᴇ.")
        
    # get[0] is the currently playing track. We only shuffle the rest.
    current_playing = get[0]
    queue = get[1:]
    
    random.shuffle(queue)
    
    # Reconstruct the queue
    anishadb[chat_id] = [current_playing] + queue
    
    await message.reply_text("🔀 **ᴏ̨ᴜᴇᴜᴇ sʜᴜғғʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**")
