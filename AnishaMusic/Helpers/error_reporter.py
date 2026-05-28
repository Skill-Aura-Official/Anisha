# MIT License
#
# Copyright (c) 2026 The Sovereign Brotherhood

import asyncio
import logging
import traceback
from datetime import datetime

LOGGER = logging.getLogger("AnishaMusic")

# Will be initialized after bot starts
_app = None
_owner_id = None

# Rate limiting: track last N errors to avoid spamming the owner
_recent_errors = []
_MAX_RECENT = 10
_COOLDOWN_SECONDS = 30  # Minimum seconds between identical error reports


def init_error_reporter(app_client, owner_id: int):
    """Initialize the error reporter with the bot client and owner ID."""
    global _app, _owner_id
    _app = app_client
    _owner_id = owner_id
    LOGGER.info(f"[ErrorReporter] Initialized → owner {owner_id}")


def _is_duplicate(error_key: str) -> bool:
    """Check if this error was recently reported (rate limiting)."""
    import time
    now = time.time()

    # Clean old entries
    global _recent_errors
    _recent_errors = [(k, t) for k, t in _recent_errors if now - t < _COOLDOWN_SECONDS]

    # Check for duplicate
    for key, _ in _recent_errors:
        if key == error_key:
            return True

    _recent_errors.append((error_key, now))

    # Keep list bounded
    if len(_recent_errors) > _MAX_RECENT:
        _recent_errors.pop(0)

    return False


async def report_error(
    module: str,
    error: Exception,
    chat_id: int = None,
    chat_title: str = None,
    user: str = None,
    extra_info: str = None,
):
    """
    Send an error/bug report directly to the bot owner's DM.

    Args:
        module: Which module/command triggered the error (e.g., "play", "watcher")
        error: The exception object
        chat_id: Optional chat ID where the error occurred
        chat_title: Optional chat title
        user: Optional user who triggered it
        extra_info: Any additional context
    """
    if not _app or not _owner_id:
        LOGGER.warning("[ErrorReporter] Not initialized, skipping error report.")
        return

    try:
        # Build error key for deduplication
        error_key = f"{module}:{type(error).__name__}:{str(error)[:100]}"
        if _is_duplicate(error_key):
            LOGGER.debug(f"[ErrorReporter] Skipping duplicate error: {error_key}")
            return

        now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        tb_text = "".join(tb)

        # Truncate traceback if too long (Telegram message limit is 4096 chars)
        if len(tb_text) > 2500:
            tb_text = tb_text[:1200] + "\n\n... [TRUNCATED] ...\n\n" + tb_text[-1200:]

        lines = [
            "🐛 **#BUG_REPORT**",
            "",
            f"⏰ `{now}`",
            f"📦 **ᴍᴏᴅᴜʟᴇ:** `{module}`",
            f"❌ **ᴇʀʀᴏʀ:** `{type(error).__name__}: {str(error)[:200]}`",
        ]

        if chat_title:
            lines.append(f"💬 **ᴄʜᴀᴛ:** {chat_title}")
        if chat_id:
            lines.append(f"🆔 **ᴄʜᴀᴛ ɪᴅ:** `{chat_id}`")
        if user:
            lines.append(f"👤 **ᴜsᴇʀ:** {user}")
        if extra_info:
            lines.append(f"📝 **ɪɴғᴏ:** {extra_info}")

        lines.append(f"\n**ᴛʀᴀᴄᴇʙᴀᴄᴋ:**\n```\n{tb_text}\n```")

        text = "\n".join(lines)

        # Final safety truncation for Telegram's 4096 char limit
        if len(text) > 4090:
            text = text[:4087] + "```"

        await _app.send_message(
            chat_id=_owner_id,
            text=text,
            disable_web_page_preview=True,
        )
        LOGGER.info(f"[ErrorReporter] Bug report sent to owner for: {module} → {type(error).__name__}")

    except Exception as e:
        # Never let the reporter itself crash the bot
        LOGGER.error(f"[ErrorReporter] Failed to send bug report: {e}")


async def report_warning(module: str, message: str):
    """Send a warning (non-exception) message to the owner."""
    if not _app or not _owner_id:
        return

    try:
        now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        text = (
            f"⚠️ **#WARNING**\n\n"
            f"⏰ `{now}`\n"
            f"📦 **ᴍᴏᴅᴜʟᴇ:** `{module}`\n\n"
            f"📄 {message}"
        )

        if len(text) > 4090:
            text = text[:4087] + "..."

        await _app.send_message(
            chat_id=_owner_id,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        LOGGER.error(f"[ErrorReporter] Failed to send warning: {e}")


async def report_restart(reason: str = "Scheduled"):
    """Notify the owner that the bot is restarting."""
    if not _app or not _owner_id:
        return

    try:
        now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        text = (
            f"🔄 **#RESTART**\n\n"
            f"⏰ `{now}`\n"
            f"📄 **ʀᴇᴀsᴏɴ:** {reason}\n\n"
            f"➻ ʙᴏᴛ ᴡɪʟʟ ʙᴇ ʙᴀᴄᴋ ɪɴ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs..."
        )
        await _app.send_message(
            chat_id=_owner_id,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        LOGGER.error(f"[ErrorReporter] Failed to send restart notification: {e}")
