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

import os
import sys

from pyrogram import filters
from pyrogram.types import Message

from config import OWNER_ID
from AnishaMusic import BOT_NAME, LOGGER, app
from AnishaMusic.Helpers.error_reporter import report_restart


@app.on_message(filters.command("restart") & filters.user(OWNER_ID))
async def restart_bot(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    msg = await message.reply_text(
        f"🔄 **ʀᴇsᴛᴀʀᴛɪɴɢ {BOT_NAME}...**\n\n"
        "➻ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴡʜɪʟᴇ ɪ ʀᴇʙᴏᴏᴛ 🥀"
    )
    LOGGER.info("[•] Restart command received. Restarting bot...")
    await report_restart("Manual restart via /restart command")
    os.execl(sys.executable, sys.executable, "-m", "AnishaMusic")
