# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

import json
import os
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AnishaMusic import app
from AnishaMusic.Helpers import buttons

PLAYLIST_FILE = "playlists.json"

def load_playlists():
    if not os.path.exists(PLAYLIST_FILE):
        return {}
    with open(PLAYLIST_FILE, "r") as f:
        return json.load(f)

def save_playlists(data):
    with open(PLAYLIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.on_message(filters.command(["addplaylist"]) & filters.private)
async def add_playlist(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("» ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ.\nᴇxᴀᴍᴘʟᴇ: `/addplaylist https://youtu.be/...`")
    url = message.command[1]
    user_id = str(message.from_user.id)
    data = load_playlists()
    
    if user_id not in data:
        data[user_id] = []
        
    if url in data[user_id]:
        return await message.reply_text("» ᴛʜɪs sᴏɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ!")
        
    if len(data[user_id]) >= 50:
        return await message.reply_text("» ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ʜᴀᴠᴇ ᴜᴘ ᴛᴏ 50 sᴏɴɢs ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ.")
        
    data[user_id].append(url)
    save_playlists(data)
    await message.reply_text("» sᴏɴɢ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ!")

@app.on_message(filters.command(["delplaylist"]) & filters.private)
async def del_playlist(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("» ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ.\nᴇxᴀᴍᴘʟᴇ: `/delplaylist https://youtu.be/...`")
    url = message.command[1]
    user_id = str(message.from_user.id)
    data = load_playlists()
    
    if user_id not in data or url not in data[user_id]:
        return await message.reply_text("» ᴛʜɪs sᴏɴɢ ɪs ɴᴏᴛ ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ!")
        
    data[user_id].remove(url)
    save_playlists(data)
    await message.reply_text("» sᴏɴɢ sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ!")

@app.on_message(filters.command(["playlist"]) & filters.private)
async def my_playlist(_, message: Message):
    user_id = str(message.from_user.id)
    data = load_playlists()
    
    if user_id not in data or not data[user_id]:
        return await message.reply_text("» ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ ɪs ᴇᴍᴘᴛʏ!")
        
    text = f"**➻ {message.from_user.mention}'s ᴘʟᴀʏʟɪsᴛ:**\n\n"
    for i, url in enumerate(data[user_id], 1):
        text += f"**{i}.** {url}\n"
        
    text += "\n» ᴜsᴇ `/playplaylist` ɪɴ ᴀ ɢʀᴏᴜᴘ ᴛᴏ ᴘʟᴀʏ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ."
    await message.reply_text(text, disable_web_page_preview=True)

@app.on_message(filters.command(["playplaylist"]) & filters.group)
async def play_playlist(_, message: Message):
    user_id = str(message.from_user.id)
    data = load_playlists()
    
    if user_id not in data or not data[user_id]:
        return await message.reply_text("» ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ ɪs ᴇᴍᴘᴛʏ! ᴀᴅᴅ sᴏɴɢs ɪɴ ᴍʏ ᴘᴍ ғɪʀsᴛ ᴜsɪɴɢ `/addplaylist`.")
        
    msg = await message.reply_text("» ǫᴜᴇᴜɪɴɢ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ...")
    # Queueing multiple songs will take time and requires modifying the play flow.
    # To keep it simple, we will execute the /play command for the first 5 songs sequentially.
    songs = data[user_id][:5] # Limit to 5 at once to avoid spamming the bot
    await msg.edit_text(f"» ǫᴜᴇᴜɪɴɢ {len(songs)} sᴏɴɢs ғʀᴏᴍ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.")
    
    from AnishaMusic.Modules.play import play_cmd
    for url in songs:
        message.text = f"/play {url}"
        message.command = ["play", url]
        try:
            await play_cmd(_, message)
        except Exception as e:
            pass
            
    await msg.edit_text(f"» sᴜᴄᴄᴇssғᴜʟʟʏ ǫᴜᴇᴜᴇᴅ {len(songs)} sᴏɴɢs ғʀᴏᴍ ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛ!")
