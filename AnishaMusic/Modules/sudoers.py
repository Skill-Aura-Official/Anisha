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

from config import OWNER_ID
from AnishaMusic import SUDOERS, MANAGERS, GBANNED_USERS, app
from AnishaMusic.Helpers.database import (
    add_cofounder_db,
    remove_cofounder_db,
    add_manager_db,
    remove_manager_db,
    add_gbanned_db,
    remove_gbanned_db,
)


@app.on_message(filters.command(["addsudo", "addcofounder"]) & filters.user(OWNER_ID))
async def sudoadd(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ ɪᴅ."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if int(user.id) in SUDOERS:
            return await message.reply_text(f"» {user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴄᴏ-ғᴏᴜɴᴅᴇʀ.")
        try:
            SUDOERS.add(int(user.id))
            add_cofounder_db(int(user.id))
            await message.reply_text(f"ᴀᴅᴅᴇᴅ {user.mention} ɪɴ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ.")
        except:
            return await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴜsᴇʀ ɪɴ ᴄᴏ-ғᴏᴜɴᴅᴇʀs.")
    else:
        user_id = message.reply_to_message.from_user.id
        if user_id in SUDOERS:
            return await message.reply_text(
                f"» {message.reply_to_message.from_user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴄᴏ-ғᴏᴜɴᴅᴇʀ."
            )
        try:
            SUDOERS.add(user_id)
            add_cofounder_db(user_id)
            await message.reply_text(
                f"ᴀᴅᴅᴇᴅ {message.reply_to_message.from_user.mention} ɪɴ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ."
            )
        except:
            return await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴜsᴇʀ ɪɴ ᴄᴏ-ғᴏᴜɴᴅᴇʀs.")


@app.on_message(filters.command(["delsudo", "rmsudo", "rmcofounder"]) & filters.user(OWNER_ID))
async def sudodel(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ ɪᴅ."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if int(user.id) not in SUDOERS:
            return await message.reply_text(
                f"» {user.mention} ɪs ɴᴏᴛ ɪɴ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ."
            )
        try:
            SUDOERS.remove(int(user.id))
            remove_cofounder_db(int(user.id))
            return await message.reply_text(
                f"» ʀᴇᴍᴏᴠᴇᴅ {user.mention} ғʀᴏᴍ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ."
            )
        except:
            return await message.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ ғʀᴏᴍ ᴄᴏ-ғᴏᴜɴᴅᴇʀs.")
    else:
        user_id = message.reply_to_message.from_user.id
        if int(user_id) not in SUDOERS:
            return await message.reply_text(
                f"» {message.reply_to_message.from_user.mention} ɪs ɴᴏᴛ ɪɴ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ."
            )
        try:
            SUDOERS.remove(int(user_id))
            remove_cofounder_db(int(user_id))
            return await message.reply_text(
                f"» ʀᴇᴍᴏᴠᴇᴅ {message.reply_to_message.from_user.mention} ғʀᴏᴍ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ."
            )
        except:
            return await message.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ ғʀᴏᴍ ᴄᴏ-ғᴏᴜɴᴅᴇʀs.")


@app.on_message(filters.command(["addmanager"]) & SUDOERS)
async def manageradd(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ ɪᴅ."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if int(user.id) in MANAGERS:
            return await message.reply_text(f"» {user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴍᴀɴᴀɢᴇʀ.")
        try:
            MANAGERS.add(int(user.id))
            add_manager_db(int(user.id))
            await message.reply_text(f"ᴀᴅᴅᴇᴅ {user.mention} ɪɴ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ.")
        except:
            return await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴜsᴇʀ ɪɴ ᴍᴀɴᴀɢᴇʀs.")
    else:
        user_id = message.reply_to_message.from_user.id
        if user_id in MANAGERS:
            return await message.reply_text(
                f"» {message.reply_to_message.from_user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴍᴀɴᴀɢᴇʀ."
            )
        try:
            MANAGERS.add(user_id)
            add_manager_db(user_id)
            await message.reply_text(
                f"ᴀᴅᴅᴇᴅ {message.reply_to_message.from_user.mention} ɪɴ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ."
            )
        except:
            return await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ᴜsᴇʀ ɪɴ ᴍᴀɴᴀɢᴇʀs.")


@app.on_message(filters.command(["rmmanager"]) & SUDOERS)
async def managerdel(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ ɪᴅ."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if int(user.id) not in MANAGERS:
            return await message.reply_text(
                f"» {user.mention} ɪs ɴᴏᴛ ɪɴ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ."
            )
        try:
            MANAGERS.remove(int(user.id))
            remove_manager_db(int(user.id))
            return await message.reply_text(
                f"» ʀᴇᴍᴏᴠᴇᴅ {user.mention} ғʀᴏᴍ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ."
            )
        except:
            return await message.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ ғʀᴏᴍ ᴍᴀɴᴀɢᴇʀs.")
    else:
        user_id = message.reply_to_message.from_user.id
        if int(user_id) not in MANAGERS:
            return await message.reply_text(
                f"» {message.reply_to_message.from_user.mention} ɪs ɴᴏᴛ ɪɴ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ."
            )
        try:
            MANAGERS.remove(int(user_id))
            remove_manager_db(int(user_id))
            return await message.reply_text(
                f"» ʀᴇᴍᴏᴠᴇᴅ {message.reply_to_message.from_user.mention} ғʀᴏᴍ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ."
            )
        except:
            return await message.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ ғʀᴏᴍ ᴍᴀɴᴀɢᴇʀs.")


@app.on_message(filters.command(["gban"]) & SUDOERS)
async def gban_user(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ ɪᴅ."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
    else:
        user = message.reply_to_message.from_user

    user_id = int(user.id)
    if user_id == OWNER_ID or user_id in SUDOERS or user_id in MANAGERS:
        return await message.reply_text("» ʏᴏᴜ ᴄᴀɴɴᴏᴛ ɢʙᴀɴ ᴀ ғᴏᴜɴᴅᴇʀ, ᴄᴏ-ғᴏᴜɴᴅᴇʀ, ᴏʀ ᴍᴀɴᴀɢᴇʀ!")
        
    if user_id in GBANNED_USERS:
        return await message.reply_text(f"» {user.mention} ɪs ᴀʟʀᴇᴀᴅʏ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ.")
        
    try:
        GBANNED_USERS.add(user_id)
        add_gbanned_db(user_id)
        await message.reply_text(f"ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ {user.mention}.")
        
        # Kick from current chat if in a group
        if message.chat.type != message.chat.type.PRIVATE:
            try:
                await message.chat.ban_member(user_id)
            except:
                pass
    except Exception as e:
        return await message.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ɢʙᴀɴ ᴜsᴇʀ: {e}")


@app.on_message(filters.command(["ungban"]) & SUDOERS)
async def ungban_user(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ ɪᴅ."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
    else:
        user = message.reply_to_message.from_user

    user_id = int(user.id)
    if user_id not in GBANNED_USERS:
        return await message.reply_text(f"» {user.mention} ɪs ɴᴏᴛ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ.")
        
    try:
        GBANNED_USERS.remove(user_id)
        remove_gbanned_db(user_id)
        await message.reply_text(f"ɢʟᴏʙᴀʟʟʏ ᴜɴʙᴀɴɴᴇᴅ {user.mention}.")
    except Exception as e:
        return await message.reply_text(f"ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴɢʙᴀɴ ᴜsᴇʀ: {e}")


@app.on_message(filters.command(["sudolist", "sudoers", "sudo", "cofounders"]))
async def sudoers_list(_, message: Message):
    hehe = await message.reply_text("» ɢᴇᴛᴛɪɴɢ ᴛsʙ ᴄᴏ-ғᴏᴜɴᴅᴇʀs ʟɪsᴛ...")
    text = "<u>👑 **ᴛsʙ ғᴏᴜɴᴅᴇʀ :**</u>\n"
    count = 0
    try:
        user = await app.get_users(OWNER_ID)
        user = user.first_name if not user.mention else user.mention
    except:
        user = f"Founder ({OWNER_ID})"
    count += 1
    text += f"{count}➤ {user}\n"
    smex = 0
    for user_id in SUDOERS:
        if user_id != OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += "\n<u>✨ **ᴛsʙ ᴄᴏ-ғᴏᴜɴᴅᴇʀs :**</u>\n"
                count += 1
                text += f"{count}➤ {user}\n"
            except Exception:
                continue
    await hehe.edit_text(text)


@app.on_message(filters.command(["managers", "managerlist"]))
async def managers_list(_, message: Message):
    hehe = await message.reply_text("» ɢᴇᴛᴛɪɴɢ ᴛsʙ ᴍᴀɴᴀɢᴇʀs ʟɪsᴛ...")
    text = ""
    count = 0
    for user_id in MANAGERS:
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            if count == 0:
                text += "<u>💼 **ᴛsʙ ᴍᴀɴᴀɢᴇʀs :**</u>\n"
            count += 1
            text += f"{count}➤ {user}\n"
        except Exception:
            continue
    if not text:
        await hehe.edit_text("» ɴᴏ ᴛsʙ ᴍᴀɴᴀɢᴇʀs ғᴏᴜɴᴅ.")
    else:
        await hehe.edit_text(text)
