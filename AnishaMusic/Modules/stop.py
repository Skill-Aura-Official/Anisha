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

from AnishaMusic import app, pytgcalls
from AnishaMusic.Helpers import _clear_, admin_check, close_key
from AnishaMusic.Helpers.logger import log_activity


@app.on_message(filters.command(["stop", "end"]) & filters.group)
@admin_check
async def stop_str(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    try:
        await _clear_(message.chat.id)
    except Exception as e:
        pass
    try:
        await pytgcalls.leave_call(message.chat.id)
    except Exception as e:
        pass
    # Force assistant to leave VC
    try:
        from AnishaMusic import app2
        await app2.send(
            raw.functions.phone.LeaveGroupCall(
                call=raw.types.InputGroupCall(id=0, access_hash=0),
            )
        )
    except:
        pass

    await log_activity(
        "STOP",
        "Stream stopped via /stop command.",
        chat_id=message.chat.id,
        chat_title=message.chat.title,
        user=message.from_user.first_name,
    )

    return await message.reply_text(
        text=f"➻ **sᴛʀᴇᴀᴍ ᴇɴᴅᴇᴅ/sᴛᴏᴩᴩᴇᴅ** ❄\n│ \n└ʙʏ : {message.from_user.mention} 🥀",
        reply_markup=close_key,
    )
