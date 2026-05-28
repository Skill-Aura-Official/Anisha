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

import asyncio
import importlib
import os
import sys

import pyrogram
from pyrogram import idle

from AnishaMusic import (
    ASS_ID,
    ASS_NAME,
    ASS_USERNAME,
    BOT_ID,
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    SUNAME,
    app,
    app2,
    pytgcalls,
)
from AnishaMusic.Modules import ALL_MODULES
from AnishaMusic.Helpers.logger import init_logger, log_activity
from AnishaMusic.Helpers.error_reporter import init_error_reporter, report_restart


async def assistant_auto_leave():
    import time
    from AnishaMusic.Helpers.active import is_active_chat
    from pyrogram.enums import ChatType
    import config

    exclude_usernames = ["TSB_Council", "TSB_Bots", "TSB_Council_Support"]
    if config.SUPPORT_CHAT:
        try:
            chat_username = config.SUPPORT_CHAT.split("t.me/")[-1].split("/")[0]
            exclude_usernames.append(chat_username)
        except:
            pass
    if config.SUPPORT_CHANNEL:
        try:
            chan_username = config.SUPPORT_CHANNEL.split("t.me/")[-1].split("/")[0]
            exclude_usernames.append(chan_username)
        except:
            pass

    inactive_since = {}

    LOGGER.info("[•] Assistant auto-leave background task started.")
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            async for dialog in app2.get_dialogs():
                chat_id = dialog.chat.id
                chat_type = dialog.chat.type
                chat_username = dialog.chat.username

                # Only monitor groups and supergroups
                if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    # Exclude official support groups
                    if chat_username and any(
                        ex.lower() == chat_username.lower() for ex in exclude_usernames
                    ):
                        continue

                    # Check if music is actively playing
                    active_stream = await is_active_chat(chat_id)
                    if not active_stream:
                        if chat_id not in inactive_since:
                            inactive_since[chat_id] = time.time()
                        elif time.time() - inactive_since[chat_id] > 3600:  # 1 hour
                            try:
                                # Don't leave if assistant is admin or owner
                                member = await app2.get_chat_member(chat_id, ASS_ID)
                                if member.status in [pyrogram.enums.ChatMemberStatus.OWNER, pyrogram.enums.ChatMemberStatus.ADMINISTRATOR]:
                                    inactive_since.pop(chat_id, None)
                                    continue
                            except Exception:
                                pass

                            try:
                                await app2.leave_chat(chat_id)
                                LOGGER.info(
                                    f"[Assistant] Left idle group: {dialog.chat.title} ({chat_id})"
                                )
                                await log_activity(
                                    "AUTO_LEAVE",
                                    f"Assistant left idle group: **{dialog.chat.title}**",
                                    chat_id=chat_id,
                                    chat_title=dialog.chat.title,
                                )
                            except Exception as e:
                                LOGGER.error(
                                    f"[Assistant] Failed to leave group {chat_id}: {e}"
                                )
                            inactive_since.pop(chat_id, None)
                    else:
                        # Music is playing, remove from idle list
                        inactive_since.pop(chat_id, None)
        except Exception as e:
            LOGGER.error(f"[Assistant] Error in auto leave loop: {e}")
            await asyncio.sleep(60)


async def startup_notify_groups():
    import config
    from AnishaMusic.Helpers.logger import log_activity
    
    # Give the bot some time to fully initialize and join chats
    await asyncio.sleep(10)
    LOGGER.info("[•] Starting group startup notifications...")
    
    startup_msg = f"""✯ **ᴀɴɪsʜᴀ ᴍᴜsɪᴄ ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ** ✯

🎶 ʜᴇʏ ᴇᴠᴇʀʏᴏɴᴇ! ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ ɪs ʙᴀᴄᴋ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ᴠɪʙᴇ 🎧

➻ ᴊᴜsᴛ ᴛʏᴘᴇ /play ᴀɴᴅ ʟᴇᴛ ᴛʜᴇ ᴍᴜsɪᴄ ᴛᴀᴋᴇ ᴏᴠᴇʀ 🔊

❛ ᴡʜᴇʀᴇ ᴇᴠᴇʀʏ ɴᴏᴛᴇ ғɪɴᴅs ɪᴛs ʜᴏᴍᴇ ❜ 🥀"""

    notified = 0
    failed = 0
    
    # Iterate through assistant's dialogs to find groups
    async for dialog in app2.get_dialogs():
        if dialog.chat.type.name in ["GROUP", "SUPERGROUP"]:
            try:
                await app.send_message(
                    chat_id=dialog.chat.id,
                    text=startup_msg
                )
                notified += 1
                await asyncio.sleep(1.5)  # Prevent flood wait
            except pyrogram.errors.FloodWait as e:
                LOGGER.warning(f"[StartupNotify] Flood wait of {e.value} seconds.")
                await asyncio.sleep(e.value + 2)
                try:
                    await app.send_message(
                        chat_id=dialog.chat.id,
                        text=startup_msg
                    )
                    notified += 1
                except Exception:
                    failed += 1
            except Exception as e:
                failed += 1
                
    LOGGER.info(f"[•] Startup notifications complete. Sent: {notified}, Failed: {failed}")
    await log_activity(
        "STARTUP_NOTIFY",
        f"Broadcasted startup message to **{notified}** groups. (Failed: {failed})"
    )


async def scheduled_restart():
    """Background task that restarts the bot daily at 5:30 AM IST (00:00 UTC)."""
    import time
    from datetime import datetime, timezone, timedelta

    # Wait for full boot
    await asyncio.sleep(30)
    LOGGER.info("[•] Scheduled restart task started (target: 05:30 AM IST / 00:00 UTC daily).")

    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            # Calculate next 00:00 UTC
            tomorrow_utc = (now_utc + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            seconds_until = (tomorrow_utc - now_utc).total_seconds()

            # If we're very close to midnight (within 60s), schedule for next day
            if seconds_until < 60:
                seconds_until += 86400

            LOGGER.info(
                f"[•] Next scheduled restart in {int(seconds_until)}s "
                f"({int(seconds_until // 3600)}h {int((seconds_until % 3600) // 60)}m)"
            )
            await asyncio.sleep(seconds_until)

            LOGGER.info("[•] Scheduled restart triggered (05:30 AM IST / 00:00 UTC).")
            await report_restart("Scheduled daily restart (05:30 AM IST)")
            await log_activity(
                "RESTART",
                "🔄 **Scheduled daily restart** (05:30 AM IST)",
            )

            # Give the notification a moment to send
            await asyncio.sleep(3)

            # Restart the bot process
            os.execl(sys.executable, sys.executable, "-m", "AnishaMusic")

        except Exception as e:
            LOGGER.error(f"[Scheduler] Error in scheduled restart: {e}")
            await asyncio.sleep(300)  # Retry after 5 min


async def anisha_startup():
    import config
    init_logger(app, config.LOG_CHANNEL_ID)
    init_error_reporter(app, config.OWNER_ID)

    LOGGER.info("[•] Loading Modules...")
    for module in ALL_MODULES:
        importlib.import_module("AnishaMusic.Modules." + module)
    LOGGER.info(f"[•] Loaded {len(ALL_MODULES)} Modules.")

    LOGGER.info("[•] Refreshing Directories...")
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    if "cache" not in os.listdir():
        os.mkdir("cache")
    LOGGER.info("[•] Directories Refreshed.")

    try:
        await app.send_message(
            SUNAME,
            f"✯ ᴀɴɪsʜᴀ ᴍᴜsɪᴄ ʙᴏᴛ ✯\n\n𖢵 ɪᴅ : `{BOT_ID}`\n𖢵 ɴᴀᴍᴇ : {BOT_NAME}\n𖢵 ᴜsᴇʀɴᴀᴍᴇ : @{BOT_USERNAME}",
        )
    except:
        LOGGER.error(
            f"{BOT_NAME} failed to send message at @{SUNAME}, please go & check."
        )

    try:
        await app2.send_message(
            SUNAME,
            f"✯ ᴛsʙ ᴄᴏᴜɴᴄɪʟ ᴀssɪsᴛᴀɴᴛ ✯\n\n𖢵 ɪᴅ : `{ASS_ID}`\n𖢵 ɴᴀᴍᴇ : {ASS_NAME}\n𖢵 ᴜsᴇʀɴᴀᴍᴇ : @{ASS_USERNAME}",
        )
    except:
        LOGGER.error(
            f"{ASS_NAME} failed to send message at @{SUNAME}, please go & check."
        )

    try:
        await app2.send_message(BOT_USERNAME, "/start")
    except:
        pass

    LOGGER.info(f"[•] Bot Started As {BOT_NAME}.")
    LOGGER.info(f"[•] Assistant Started As {ASS_NAME}.")

    LOGGER.info(
        "[•] \x53\x74\x61\x72\x74\x69\x6e\x67\x20\x50\x79\x54\x67\x43\x61\x6c\x6c\x73\x20\x43\x6c\x69\x65\x6e\x74\x2e\x2e\x2e"
    )
    await pytgcalls.start()

    # Flush any stale/pending updates from previous sessions
    try:
        await app.invoke(
            pyrogram.raw.functions.updates.GetState()
        )
    except:
        pass

    asyncio.create_task(assistant_auto_leave())
    asyncio.create_task(startup_notify_groups())
    asyncio.create_task(scheduled_restart())
    LOGGER.info("[•] Bot is now READY and listening for commands!")
    await log_activity(
        "STARTUP",
        f"🚀 **Anisha Music Bot Started**\n\n𖢵 **Bot:** {BOT_NAME} (@{BOT_USERNAME})\n𖢵 **Assistant:** {ASS_NAME} (@{ASS_USERNAME})\n𖢵 **Modules:** {len(ALL_MODULES)}",
    )
    await idle()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(anisha_startup())
    LOGGER.error("Anisha Music Bot Stopped.")
