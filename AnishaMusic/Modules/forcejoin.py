from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram import StopPropagation
from AnishaMusic import app, SUDOERS, MANAGERS, GBANNED_USERS, BOT_MENTION
from AnishaMusic.Helpers.inline import pm_buttons
from AnishaMusic.Helpers.dossier import PM_START_TEXT
import config

# Intercept Globally Banned Users (Priority Group -2)
@app.on_message(filters.incoming & ~filters.service, group=-2)
async def gban_intercept_handler(client: Client, message: Message):
    if not message.from_user:
        return
    
    if message.from_user.id in GBANNED_USERS:
        if message.chat.type == message.chat.type.PRIVATE:
            await message.reply_text("🚨 **ʏᴏᴜ ᴀʀᴇ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ!**")
        else:
            try:
                await message.chat.ban_member(message.from_user.id)
                await message.reply_text(
                    f"🚨 **ɢʙᴀɴɴᴇᴅ ᴜsᴇʀ ᴅᴇᴛᴇᴄᴛᴇᴅ!**\n\n➻ {message.from_user.mention} has been banned from the chat."
                )
            except Exception:
                pass
        raise StopPropagation

# Force Subscription for DMs (Priority Group -1)
@app.on_message(filters.private & ~filters.service, group=-1)
async def force_join_check_handler(client: Client, message: Message):
    if not message.from_user:
        return

    # Skip Founder (Owner) and Co-founders (SUDOERS)
    if message.from_user.id in SUDOERS or message.from_user.id == config.OWNER_ID:
        return
    
    not_joined = []
    
    # Check Bots Channel
    try:
        member = await client.get_chat_member("TSB_Bots", message.from_user.id)
        if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
            not_joined.append(("Bots Channel", "https://t.me/TSB_Bots"))
    except UserNotParticipant:
        not_joined.append(("Bots Channel", "https://t.me/TSB_Bots"))
    except Exception:
        pass
        
    # Check Support Group
    try:
        member = await client.get_chat_member("TSB_Council_Support", message.from_user.id)
        if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
            not_joined.append(("Support Group", "https://t.me/TSB_Council_Support"))
    except UserNotParticipant:
        not_joined.append(("Support Group", "https://t.me/TSB_Council_Support"))
    except Exception:
        pass
        
    if not_joined:
        buttons = []
        for name, link in not_joined:
            buttons.append([InlineKeyboardButton(text=f"Join {name}", url=link)])
        buttons.append([InlineKeyboardButton(text="🔄 Try Again / Check", callback_data="check_force_join")])
        
        await message.reply_text(
            text=(
                f"👋 **ʜᴇʏ {message.from_user.first_name} !**\n\n"
                f"๏ ᴛᴏ ᴜsᴇ **ᴀɴɪsʜᴀ** (ᴍᴜsɪᴄ ʙᴏᴛ) ɪɴ ᴅᴍ, ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ **ʙᴏᴛs ᴄʜᴀɴɴᴇʟ** & **sᴜᴩᴩᴏʀᴛ ɢʀᴏᴜᴩ**.\n\n"
                f"➻ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ ᴀɴᴅ ᴄʟɪᴄᴋ **ᴛʀʏ ᴀɢᴀɪɴ** ᴛᴏ sᴛᴀʀᴛ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ."
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        raise StopPropagation

# Callback Handler for Try Again / Check button
@app.on_callback_query(filters.regex("check_force_join"))
async def check_force_join_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    not_joined = []
    
    # Check Bots Channel
    try:
        member = await client.get_chat_member("TSB_Bots", user_id)
        if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
            not_joined.append(("Bots Channel", "https://t.me/TSB_Bots"))
    except UserNotParticipant:
        not_joined.append(("Bots Channel", "https://t.me/TSB_Bots"))
    except Exception:
        pass
        
    # Check Support Group
    try:
        member = await client.get_chat_member("TSB_Council_Support", user_id)
        if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
            not_joined.append(("Support Group", "https://t.me/TSB_Council_Support"))
    except UserNotParticipant:
        not_joined.append(("Support Group", "https://t.me/TSB_Council_Support"))
    except Exception:
        pass
        
    if not_joined:
        await query.answer("❌ You still have not joined all the required channels/groups!", show_alert=True)
    else:
        await query.message.delete()
        await query.answer("✅ Thank you for joining! You can now use the bot.", show_alert=True)
        
        # Send PM welcome / start message
        await client.send_message(
            chat_id=query.message.chat.id,
            text=PM_START_TEXT.format(
                query.from_user.first_name,
                BOT_MENTION,
            ),
            reply_markup=InlineKeyboardMarkup(pm_buttons),
        )
