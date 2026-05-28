# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

import asyncio
import logging
from datetime import datetime

LOGGER = logging.getLogger("AnishaMusic")

# Will be initialized after bot starts
_app = None
_log_channel = None


def init_logger(app_client, log_channel_id: int):
    """Initialize the logger with the bot client and log channel ID."""
    global _app, _log_channel
    _app = app_client
    _log_channel = log_channel_id
    LOGGER.info(f"[Logger] Activity logger initialized → channel {log_channel_id}")
    
    # Start the periodic active groups logger task
    asyncio.create_task(_active_groups_loop())


async def log_active_groups_list():
    """Fetches currently active voice chats and logs the list to the channel."""
    if not _app or not _log_channel:
        return
    from AnishaMusic.Helpers.active import get_active_chats
    
    try:
        chats = await get_active_chats()
        if not chats:
            text = "👥 **#ACTIVE_GROUPS**\n\nNo active voice chats currently running."
        else:
            lines = ["👥 **#ACTIVE_GROUPS**", f"Currently running in `{len(chats)}` groups:\n"]
            for i, chat_id in enumerate(chats, 1):
                try:
                    chat = await _app.get_chat(chat_id)
                    title = chat.title
                    username = chat.username
                    if username:
                        lines.append(f"{i}. [{title}](https://t.me/{username}) (`{chat_id}`)")
                    else:
                        lines.append(f"{i}. **{title}** (`{chat_id}`)")
                except Exception:
                    lines.append(f"{i}. Unknown Chat (`{chat_id}`)")
            text = "\n".join(lines)
            
        await _app.send_message(
            chat_id=_log_channel,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        LOGGER.error(f"[Logger] Failed to log active groups: {e}")


async def _active_groups_loop():
    # Wait for the bot client to finish boot phase
    await asyncio.sleep(45)
    while True:
        try:
            await log_active_groups_list()
        except Exception as e:
            LOGGER.error(f"[Logger] Error in active groups loop: {e}")
        # Log every 2 hours
        await asyncio.sleep(7200)


async def log_activity(
    event_type: str,
    details: str,
    chat_id: int = None,
    chat_title: str = None,
    user: str = None,
):
    """
    Send an activity log message to the log channel.
    Only allows specific high-value logs (START, JOINED_GROUP, ACTIVE_GROUPS).
    """
    if not _app or not _log_channel:
        return

    # Filter to ONLY allow the three user-requested log types
    ALLOWED_EVENTS = {"START", "JOINED_GROUP", "ACTIVE_GROUPS", "RESTART", "STARTUP"}
    if event_type not in ALLOWED_EVENTS:
        LOGGER.debug(f"[Activity Log Suppressed] #{event_type} - {details}")
        return

    now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    icon_map = {
        "START": "👤",
        "JOINED_GROUP": "📥",
        "ACTIVE_GROUPS": "👥",
    }
    icon = icon_map.get(event_type, "📝")

    lines = [f"{icon} **#{event_type}**", ""]
    lines.append(f"⏰ `{now}`")

    if chat_title:
        lines.append(f"💬 **ᴄʜᴀᴛ:** {chat_title}")
    if chat_id:
        lines.append(f"🆔 `{chat_id}`")
    if user:
        lines.append(f"👤 **ʙʏ:** {user}")

    lines.append(f"\n📄 {details}")

    text = "\n".join(lines)

    try:
        await _app.send_message(
            chat_id=_log_channel,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        LOGGER.error(f"[Logger] Failed to send log to channel: {e}")
