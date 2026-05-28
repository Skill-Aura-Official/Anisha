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
import random

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait, ChatAdminRequired, PeerIdInvalid
from pyrogram.types import Message

from AnishaMusic import app, LOGGER, BOT_ID, ASS_ID, SUDOERS

# ─────────────── Active Sessions Tracker ───────────────
# Tracks active tagging sessions per chat to prevent duplicates & allow cancel
_active_tag_sessions = {}


# ─────────────── 200 Unique Tag Messages (Cool Hinglish) ───────────────
TAG_MESSAGES = [
    # ── Hype & Energy ──
    "🔥 ᴀʀʀᴇ ᴏʏᴇ, ᴋʏᴀ ᴋᴀʀ ʀᴀʜᴇ ʜᴏ sᴀʙ?",
    "⚡ ᴊᴀʟᴅɪ ᴀᴀᴏ, sᴄᴇɴᴇ ᴏɴ ʜᴀɪ!",
    "🚀 ᴋɪᴅʜᴀʀ ɢᴀᴀʏᴀʙ ʜᴏ sᴀᴀʀᴇ?",
    "💥 ʙᴏᴏᴍ! sᴀʙ ᴏɴʟɪɴᴇ ᴀᴀᴏ!",
    "🎯 ʀᴏʟʟ ᴄᴀʟʟ! ʜᴀᴀᴢɪʀɪ ʟᴀɢᴀᴏ!",
    "🏆 ᴄʜᴀᴍᴘɪᴏɴs ᴋᴀʜᴀɴ ʜᴀɪ?",
    "💪 ɢᴀɴɢ, ᴡᴀᴋᴇ ᴜᴘ!",
    "🌟 ᴀsʟɪ sᴛᴀʀs ᴛᴏʜ ʏᴀʜᴀɴ ʜᴀɪ!",
    "🎪 ᴍᴇʜғɪʟ sᴀᴊᴀ ᴅᴏ!",
    "⭐ ʙʜᴀᴜᴋᴀᴀʟ ᴍᴀᴄʜᴀ ᴅᴏ!",
    "🔔 ᴛʀɪɴɢ ᴛʀɪɴɢ! ᴜᴛʜ ᴊᴀᴏ!",
    "🎆 ᴀᴀɢ ʟᴀɢᴀ ᴅᴇɴɢᴇ ᴀᴀɢ!",
    "💫 sʜᴏᴡ ᴛɪᴍᴇ ʜᴀɪ ʙɪᴅᴜ!",
    "🦁 sʜᴇʀ ᴊᴀᴀɢ ɢᴀʏᴇ ᴋʏᴀ?",
    "🐉 ᴛᴀʙᴀᴀʜɪ ᴍᴀᴄʜᴀɴᴇ ᴀᴀᴏ!",
    "🎸 ʀᴏᴄᴋ ᴋᴀʀ ᴅᴏ!",
    "🔊 ᴀᴀᴡᴀᴀᴢ ɴᴀʜɪ ᴀᴀ ʀᴀʜɪ!",
    "⚔️ ʏᴏᴅᴅʜᴀᴏ, ʙᴀʜᴀʀ ᴀᴀᴏ!",
    "🎭 ᴄʜᴇʜʀᴇ ᴅɪᴋʜᴀᴏ ᴀᴘɴᴇ!",
    "💎 ʜᴇᴇʀᴏ ᴋᴀʜᴀɴ ᴄʜʜᴜᴘᴇ ʜᴏ?",

    # ── Music & Vibe ──
    "🎵 ᴍᴜsɪᴄ ᴏɴ, ᴅᴜɴɪʏᴀ ɢᴏɴᴇ!",
    "🎶 ʙᴇᴀᴛ ᴘᴇ ʙᴏᴏᴛʏ!",
    "🎧 ᴠɪʙᴇ ᴄʜᴇᴄᴋ ᴋᴀʀʟᴏ sᴀʙ!",
    "🎤 ᴋᴏɪ ɢᴀᴀɴᴀ sᴜɴᴀᴏ ʏᴀᴀʀ!",
    "🎹 ᴘɪᴀɴᴏ ʙᴀᴊ ʀᴀʜᴀ ʜᴀɪ!",
    "🥁 ᴅʜᴏʟ ʙᴀᴊᴀᴏ ʀᴇ ᴋᴏɪ!",
    "📻 ғᴍ ᴏɴ ʜᴀɪ!",
    "🎺 ʙᴀᴀᴊᴀ ʙᴀʀᴀᴀᴛ ʀᴇᴀᴅʏ ʜᴀɪ!",
    "💿 ᴅᴊ ᴡᴀʟᴇ ʙᴀʙᴜ ᴍᴇʀᴀ ɢᴀᴀɴᴀ ʙᴀᴊᴀ ᴅᴏ!",
    "🎻 sᴜʀ ᴏʀ ᴛᴀᴀʟ ᴍɪʟᴀᴏ!",
    "🎼 sᴜʀɪʟᴇ ʟᴏɢᴏ, ᴀᴀᴊᴀᴏ!",
    "🔉 ᴛʜᴏᴅᴀ sʜᴏʀ ᴍᴀᴄʜᴀᴏ!",
    "🎙️ ᴍᴀɪᴋ ᴛᴇsᴛɪɴɢ, ᴀᴡᴀᴀᴢ ᴀᴀ ʀᴀʜɪ ʜᴀɪ?",
    "🎷 ᴊᴀᴢᴢ ᴠɪʙᴇs ᴏɴʟʏ!",
    "🪗 ᴅɪʟ ᴋᴇ ᴛᴀᴀʀ ᴄʜʜᴇᴅ ᴅɪʏᴇ!",
    "🎵 ᴀᴀᴘᴋɪ ᴘғᴘ ʙᴀᴡᴀᴀʟ ʜᴀɪ!",
    "🎶 ɢᴀᴀɴᴀ ᴄʜᴀɴɢᴇ ᴋᴀʀᴏ ᴋᴏɪ!",
    "🎧 ʜᴇᴀᴅᴘʜᴏɴᴇs ʟᴀɢᴀ ʟɪʏᴇ?",
    "🎤 ᴀᴀᴊ ᴍᴀɪɴ ɢᴀᴀᴜɴɢᴀ!",
    "💿 ᴘᴀʀᴛʏ ᴀʙʜɪ ʙᴀᴀᴋɪ ʜᴀɪ!",

    # ── Group Revival ──
    "💀 ᴢɪɴᴅᴀ ʜᴏ ʏᴀ ɴɪᴘᴀᴛ ɢᴀʏᴇ?",
    "👻 ʙʜᴏᴏᴛ ʙᴀɴ ɢᴀʏᴇ ᴋʏᴀ sᴀʙ?",
    "🧟 ᴍᴜʀᴅᴏ, ᴊᴀᴀɢ ᴊᴀᴏ!",
    "🪦 ɢʀᴏᴜᴘ ᴍᴀʀ ɢᴀʏᴀ ᴋʏᴀ?",
    "🌅 sᴜʙᴀʜ ʜᴏ ɢᴀʏɪ ᴍᴀᴍᴜ!",
    "🌊 ʙᴀᴀᴅʜ ʟᴀᴀ ᴅᴏ ᴍᴇssᴀɢᴇs ᴋɪ!",
    "🔓 ᴛᴀᴀʟᴀ ᴋʜᴜʟ ɢᴀʏᴀ ʜᴀɪ!",
    "📢 ᴀᴛᴛᴇɴᴛɪᴏɴ ᴘʟᴇᴀsᴇ!",
    "🗣️ ᴋᴜᴄʜ ᴛᴏ ʙᴏʟᴏ ʏᴀᴀʀ!",
    "💬 ᴄʜᴀᴛ ᴋᴀʀ ʟᴏ ᴛʜᴏᴅᴀ!",
    "🌍 ᴅᴜɴɪʏᴀ ᴅᴇᴋʜ ʀᴀʜɪ ʜᴀɪ ᴛᴜᴍʜᴇɪɴ!",
    "🏟️ ᴍᴀɪᴅᴀᴀɴ ᴍᴇɪɴ ᴀᴀᴏ!",
    "🎪 ᴛᴀᴍᴀsʜᴀ sʜᴜʀᴜ ᴋᴀʀᴇɪɴ?",
    "🌋 ᴊᴡᴀʟᴀᴍᴜᴋʜɪ ғᴀᴛɴᴇ ᴡᴀʟᴀ ʜᴀɪ!",
    "🎇 ᴅɪᴡᴀʟɪ ᴀᴀᴊ ʜɪ ᴍᴀɴᴀʏᴇɴɢᴇ!",
    "📣 ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ ʜᴀɪ ᴇᴋ!",
    "🏰 ʀᴀᴊᴀ ᴊɪ ᴀᴀ ɢᴀʏᴇ!",
    "🌪️ ᴛᴏᴏғᴀᴀɴ ʟᴀᴀᴏ!",
    "🔔 ɢʜᴀɴᴛɪ ʙᴀᴊᴀᴏ ɪɴᴋɪ!",
    "💣 ʙᴀᴍ ғᴏᴅ ᴅᴇɴɢᴇ!",

    # ── Funny & Savage ──
    "👀 ᴋᴀᴜɴ ᴋᴀᴜɴ ᴏɴʟɪɴᴇ ʜᴀɪ?",
    "🤡 sᴀʙsᴇ ʙᴀᴅᴇ ɴᴀʟʟᴇ ᴀᴀɢᴀʏᴇ!",
    "🐒 ʙᴀɴᴅᴀʀ ᴋʏᴀ ᴊᴀᴀɴᴇ ᴀᴅʀᴀᴋ ᴋᴀ sᴡᴀᴀᴅ!",
    "🐸 ᴍᴇɴᴅʜᴀᴋ ᴋɪ ᴛᴀʀᴀʜ ᴜᴄʜʟᴏ ᴍᴀᴛ!",
    "🍕 ᴘɪᴢᴢᴀ ᴋʜᴀᴀ ʀᴀʜᴇ ʜᴏ ᴀᴋᴇʟᴇ ᴀᴋᴇʟᴇ?",
    "🍔 ʙʜᴏᴏᴋʜ ʟᴀɢɪ ʜᴀɪ ᴋʏᴀ?",
    "🧠 ᴅɪᴍᴀᴀɢ ʟᴀɢᴀᴏ ᴛʜᴏᴅᴀ!",
    "🤓 ᴘᴀᴅʜᴀᴋᴜ ʟᴏɢᴏ, ᴄʜʜᴜᴛᴛɪ ʜᴀɪ ᴀᴀᴊ!",
    "😴 sᴏ ʀᴀʜᴇ ʜᴏ ᴋʏᴀ?",
    "🫣 ᴄʜʜᴜᴘᴏ ᴍᴀᴛ ᴍᴜᴊʜsᴇ!",
    "🥱 ᴜʙᴀᴀsɪ ᴍᴀᴛ ʟᴏ, ᴛʏᴘᴇ ᴋᴀʀᴏ!",
    "🤫 sʜʜʜ... ᴋᴏɪ ᴅᴇᴋʜ ʟᴇɢᴀ!",
    "😏 ʟᴜʀᴋᴇʀs ᴋᴏ ᴘᴀᴋᴀᴅ ʟɪʏᴀ!",
    "🫡 ʜᴀᴀᴢɪʀ ʜᴏ ᴊᴀᴀᴏ!",
    "🧊 ʙᴀʀᴀғ ᴊᴀᴍ ɢᴀʏɪ ʜᴀɪ ᴋʏᴀ ʜᴀᴀᴛʜᴏ ᴍᴇɪɴ?",
    "🎃 ᴅᴀʀ ɢᴀʏᴇ ᴋʏᴀ?",
    "🤭 ʙᴜsʏ ʜᴏɴᴇ ᴋᴀ ɴᴀᴛᴀᴋ ᴍᴀᴛ ᴋᴀʀᴏ!",
    "🫠 ᴘɪɢʜᴀʟ ɢᴀʏᴇ ᴍᴇʀɪ ʙᴀᴀᴛᴏɴ sᴇ?",
    "🧐 ᴋɪsᴋɪ ʏᴀᴀᴅ ᴀᴀ ʀᴀʜɪ ʜᴀɪ?",
    "🎩 sʏsᴛᴜᴍ ʜᴀɴɢ ᴋᴀʀ ᴅɪʏᴀ ɴᴀ!",

    # ── Motivation & Cool ──
    "🏋️ ɢʏᴍ ᴊᴀᴀᴏ, ᴅᴏʟᴇ-sʜᴏʟᴇ ʙᴀɴᴀᴏ!",
    "🎖️ ɪᴢᴢᴀᴛ ᴋᴀᴍᴀᴏ ᴘᴇʜʟᴇ!",
    "🏅 ɢᴏʟᴅ ᴍᴇᴅᴀʟ ʟᴀᴀʏᴇɢᴀ ᴍᴇʀᴀ ʙʜᴀɪ!",
    "🌈 ʀᴀɴɢ ʙʜᴀʀ ᴅᴏ ᴢɪɴᴅᴀɢɪ ᴍᴇɪɴ!",
    "🕊️ ᴘᴇᴀᴄᴇ ᴏᴜᴛ ʙʀᴏ!",
    "🗺️ ɴᴀᴋsʜᴀ ᴋʜᴏ ɢᴀʏᴀ ᴋʏᴀ?",
    "🧭 ʀᴀsᴛᴀ ʙʜᴀᴛᴀᴋ ɢᴀʏᴇ?",
    "🎢 ʀᴏʟʟᴇʀᴄᴏᴀsᴛᴇʀ ᴡᴀʟɪ ғᴇᴇʟɪɴɢ!",
    "🏄 ʟᴇʜʀᴏ ᴋᴇ sᴀᴀᴛʜ ʙᴀʜᴏ!",
    "🎿 ʙᴀʀᴀғ ᴘᴇ ғɪsᴀʟ ɢᴀʏᴇ!",
    "🚂 ᴄʜʜᴜᴋ ᴄʜʜᴜᴋ ɢᴀᴀᴅɪ!",
    "✈️ ᴜᴅᴀᴀɴ ʙʜᴀʀᴏ!",
    "🛸 ᴇʟɪᴇɴ ᴜᴛʜᴀ ʟᴇ ɢᴀʏᴇ ᴋʏᴀ?",
    "🚁 ʜᴇʟɪᴄᴏᴘᴛᴇʀ ᴍᴇɪɴ ɢʜᴜᴍᴀᴀᴜɴɢᴀ!",
    "🏎️ ʀᴇs ʟᴀɢᴀ ʟᴇ ʙʜᴀɪ!",
    "🛶 ɴᴀᴀᴠ ᴅᴏᴏʙ ʀᴀʜɪ ʜᴀɪ!",
    "🗻 ᴘᴀʜᴀᴀᴅ ᴄʜᴀᴅ ᴊᴀᴀᴏ!",
    "🌠 ᴛᴏᴏᴛ'ᴛᴀ ᴛᴀᴀʀᴀ ᴅᴇᴋʜ ʟɪʏᴀ!",
    "🌙 ᴄʜᴀᴀɴᴅ ᴛᴀᴀʀᴇ ᴛᴏᴅ ʟᴀᴀᴜɴ!",
    "☀️ ᴅʜᴏᴏᴘ sᴇᴋ ʟᴏ!",

    # ── Gaming / Action ──
    "🎮 ᴀᴀᴊᴀᴏ 1ᴠ1 ᴋᴀʀʟᴇ!",
    "🕹️ ᴘᴜsʜ ᴋᴀʀ ᴅᴏ ʀᴜsʜ ᴋᴀʀ ᴅᴏ!",
    "🏹 ɴɪsʜᴀᴀɴᴀ ʟᴀɢᴀᴏ!",
    "⚔️ ᴛᴀʟᴡᴀᴀʀ ɴɪᴋᴀᴀʟᴏ ᴀᴘɴɪ!",
    "🛡️ ᴅᴇғᴇɴᴅ ᴋᴀʀᴏ ʙʜᴀɪ!",
    "🗡️ ᴋᴀᴀᴛ ᴅᴀᴀʟᴏ sᴀʙᴋᴏ!",
    "🎲 ᴋɪsᴍᴀᴛ ᴋᴀ ᴋʜᴇʟ ʜᴀɪ sᴀʙ!",
    "♟️ sʜᴇʜ ᴀᴜʀ ᴍᴀᴀᴛ!",
    "🃏 ᴊᴏᴋᴇʀ ᴋɪ ᴇɴᴛʀʏ!",
    "🎯 ᴇᴋ ʜᴇᴀᴅsʜᴏᴛ!",
    "🏰 ǫᴜɪʟᴀ ғᴀᴛᴇʜ ᴋᴀʀᴏ!",
    "🐲 ᴅʀᴀɢᴏɴ ᴋᴏ ᴍᴀᴀʀ ɢɪʀᴀᴀᴏ!",
    "🧙 ᴊᴀᴀᴅᴜ ᴅɪᴋʜᴀᴏ!",
    "🦸 sᴜᴘᴇʀʜᴇʀᴏ ᴋɪ ᴇɴᴛʀʏ!",
    "🧛 ᴋʜᴏᴏɴ ᴘᴇᴇ ᴊᴀᴀᴜɴɢᴀ!",
    "🧟 ᴢᴏᴍʙɪᴇ ʙᴀɴ ɢᴀʏᴇ sᴀʙ!",
    "🏴‍☠️ ʟᴏᴏᴛ ʟᴏ sᴀʙ ᴋᴜᴄʜ!",
    "🤺 ᴀᴀ ᴊᴀ ʙʜɪᴅ ʟᴇ!",
    "🥊 ᴍᴜᴋᴋᴀ ᴍᴀᴀʀᴜɴɢᴀ!",
    "🥋 ᴋᴀʀᴀᴛᴇ ᴄʜᴏᴘ!",

    # ── Brotherhood / Team ──
    "👑 ᴀᴘɴᴀ ᴛɪᴍᴇ ᴀᴀʏᴇɢᴀ!",
    "🤝 ʙʜᴀɪᴄʜᴀᴀʀᴀ ᴏɴ ᴛᴏᴘ!",
    "💯 sᴀᴜ ᴛᴀᴋᴀ ʙᴀᴀᴛ sᴀʜɪ!",
    "🫂 ɢᴀʟᴇ ᴍɪʟ ʟᴏ ʏᴀᴀʀ!",
    "🔗 ᴇᴋᴛᴀ ᴍᴇɪɴ ʙᴀʟ ʜᴀɪ!",
    "🤜🤛 ᴛᴇᴀᴍ ᴡᴏʀᴋ ᴍᴀᴋᴇs ᴅʀᴇᴀᴍ ᴡᴏʀᴋ!",
    "👊 ʙʜᴀɪ ʙʜᴀɪ!",
    "🙌 ʜᴀᴀᴛʜ ᴜᴘᴀʀ!",
    "✊ ᴅᴜsʜᴍᴀɴ ᴋɪ ᴄʜʜᴜᴛᴛɪ!",
    "🦅 ʙᴀᴀᴢ ᴋɪ ɴᴀᴢᴀʀ!",
    "🐺 ʙʜᴇᴅɪʏᴇ ᴀᴀ ɢᴀʏᴇ!",
    "🦈 sʜᴀʀᴋ ᴊᴀɪsᴀ ᴀᴛᴛɪᴛᴜᴅᴇ!",
    "🦅 ᴜᴅᴛᴀ ᴛᴇᴇʀ ʟᴇ ʟɪʏᴀ!",
    "🐝 ᴍᴀᴋᴋʜɪ ᴋɪ ᴛᴀʀᴀʜ ʙʜɪɴʙʜɪɴᴀᴏ ᴍᴀᴛ!",
    "🐜 ᴄʜᴇᴇɴᴛɪ ʙʜɪ ʜᴀᴀᴛʜɪ ᴋᴏ ʜᴀʀᴀ sᴀᴋᴛɪ ʜᴀɪ!",
    "🦋 ᴛɪᴛʟɪ ᴋɪ ᴛᴀʀᴀʜ ᴜᴅᴏ!",
    "🐋 ʙᴀᴅɪ ᴍᴀᴄʜʜʟɪ!",
    "🦊 ʟᴏᴍᴅɪ ᴊᴀɪsɪ ᴄʜᴀᴀʟᴀᴀᴋɪ!",
    "🐧 ᴘᴇɴɢᴜɪɴ sᴇ ᴘʏᴀᴀʀᴇ ʜᴏ sᴀʙ!",
    "🐼 ᴘᴀɴᴅᴀ ᴊᴀɪsᴇ ᴀᴀʟsɪ!",

    # ── Random Fun ──
    "🌮 ᴋʜᴀᴀɴᴇ ᴍᴇɪɴ ᴋʏᴀ ʜᴀɪ ᴀᴀᴊ?",
    "🍩 ᴍᴇᴇᴛʜᴀ ᴋʜᴀᴀ ʟᴏ ᴛʜᴏᴅᴀ!",
    "🧁 ᴄᴜᴘᴄᴀᴋᴇ ᴊᴀɪsɪ sᴍɪʟᴇ ʜᴀɪ!",
    "🍿 ᴘᴏᴘᴄᴏʀɴ ʟᴀᴀᴏ ᴋᴏɪ ᴍᴀᴢᴀ ᴀᴀʏᴇɢᴀ!",
    "🍦 ɪᴄᴇ ᴄʀᴇᴀᴍ ᴋʜɪʟᴀ ᴅᴏ!",
    "🧋 ᴄʜᴀʏ ᴘᴇᴇ ʟᴏ ғʀɪᴇɴᴅs!",
    "☕ ᴄᴏғғᴇᴇ ᴅᴀᴛᴇ ᴘᴇ ᴄʜᴀʟᴇɪɴ?",
    "🍵 ɢʀᴇᴇɴ ᴛᴇᴀ ᴘɪʏᴏ ᴘᴀᴛʟᴇ ʜᴏɢᴇ!",
    "🥤 ᴘʏᴀᴀs ʟᴀɢɪ ʜᴀɪ ᴍᴜᴊʜᴇ!",
    "🫖 ᴄʜᴜɢʟɪ ᴋᴀʀᴇɪɴ?",
    "🍰 ᴄᴀᴋᴇ ᴋᴀᴛᴇɢᴀ sᴀʙ ᴍᴇɪɴ ʙᴀᴛᴇɢᴀ!",
    "🎂 ʜᴀᴘᴘʏ ʙɪʀᴛʜᴅᴀʏ ᴛᴏ ʏᴏᴜ!",
    "🥂 ᴄʜᴇᴇʀs ʙʜᴀɪ!",
    "🍻 ᴅᴀʀᴜ ʙᴀᴅɴᴀᴀᴍ ᴋᴀʀᴛɪ ʜᴀɪ!",
    "🧃 ғʀᴏᴏᴛɪ ᴘᴇᴇ ʟᴏ!",
    "🎈 ɢᴜʙʙᴀʀᴇ ғᴏᴅᴏ!",
    "🎀 ʀɪʙʙᴏɴ ᴋᴀᴀᴛᴏ!",
    "🎁 ɢɪғᴛ ᴋᴀʜᴀɴ ʜᴀɪ ᴍᴇʀᴀ?",
    "🪅 ᴘɪɴᴀᴛᴀ ғᴏᴅ ᴅᴏ!",
    "🎊 ᴄᴏɴғᴇᴛᴛɪ ᴜᴅᴀᴀᴏ!",

    # ── Savage & Spicy ──
    "🌶️ ᴍɪʀᴄʜɪ ʟᴀɢɪ ᴋʏᴀ?",
    "🔥 ᴊᴀʟᴏ ᴍᴀᴛ ʙʀᴀʙᴀʀɪ ᴋᴀʀᴏ!",
    "🌪️ ʙʜᴀᴡᴀɴᴅᴀʀ ʟᴀᴀ ᴅᴜɴɢᴀ ʙʜᴀᴡᴀɴᴅᴀʀ!",
    "💅 ᴀᴛᴛɪᴛᴜᴅᴇ ᴅᴇᴋʜ ʀᴀʜᴇ ʜᴏ?",
    "😈 sʜᴀʀᴀᴀʀᴀᴛ ᴋᴀʀɴᴇ ᴋᴀ ᴍᴀɴ ʜᴀɪ!",
    "👹 ʀᴀᴋsʜᴀs ʜᴏ ᴛᴜᴍ sᴀʙ!",
    "🦄 ᴊᴀᴀᴅᴜɪ ɢʜᴏᴅᴀ ᴀᴀ ɢᴀʏᴀ!",
    "🐍 ᴀᴀsᴛᴇᴇɴ ᴋᴇ sᴀᴀɴᴘ!",
    "🕷️ sᴘɪᴅᴇʀᴍᴀɴ ᴋɪ ʙᴀʜᴇɴ!",
    "🦂 ᴅᴀɴᴋ ᴍᴀᴀʀ ᴅᴜɴɢᴀ!",
    "🐊 ᴍᴀɢᴀʀᴍᴀᴄʜ ᴋᴇ ᴀᴀɴsᴜ!",
    "💀 ᴋʜᴏᴘᴅɪ ғᴏᴅ sᴀᴀʟᴇ ᴋɪ!",
    "☠️ ᴋʜᴀᴛʀᴇ ᴋɪ ɢʜᴀɴᴛɪ!",
    "🧨 ᴘᴀᴛᴀᴀᴋʜᴇ ғᴏᴅᴏ ᴅɪᴡᴀʟɪ ʜᴀɪ!",
    "💣 ᴀʙʜɪ ᴛᴏʜ ʙᴀᴡᴀᴀʟ ʜᴏɢᴀ!",
    "⚠️ sᴀᴀᴠᴅʜᴀᴀɴ ʀᴀʜᴇ, sᴀᴛᴀʀᴋ ʀᴀʜᴇ!",
    "🚨 ᴘᴏʟɪᴄᴇ ᴋᴏ ʙᴜʟᴀᴏ ᴋᴏɪ!",
    "🔴 ʟᴀᴀʟ ʀᴀɴɢ ᴋʜᴀᴛʀᴇ ᴋᴀ!",
    "🟡 ᴘᴇᴇʟᴀ ʀᴀɴɢ ᴅᴏsᴛɪ ᴋᴀ!",
    "🟢 ʜᴀʀɪ ᴊʜᴀɴᴅɪ ᴍɪʟ ɢᴀʏɪ ʜᴀɪ!",

    # ── Wholesome & Chill ──
    "🥀 ᴋʏᴀ ʜᴀᴀʟ ʜᴀɪ ᴍᴇʀᴇ ᴅᴏsᴛᴏɴ?",
    "❤️ ᴅɪʟ sᴇ ᴘʏᴀᴀʀ ᴀᴀᴘ sᴀʙᴋᴏ!",
    "💕 ᴛᴜᴍ ᴍᴇʀᴇ ʙʜᴀɪ ʜᴏ ʏᴀᴀʀ!",
    "🌸 ᴘʜᴏᴏʟᴏɴ ᴋɪ ᴛᴀʀᴀʜ ᴍᴜsᴋᴜʀᴀᴏ!",
    "🌻 ᴅʜᴏᴏᴘ ᴋʜɪʟ ɢᴀʏɪ ᴀᴀᴊ!",
    "🌹 ᴇᴋ ɢᴜʟᴀᴀʙ ᴀᴀᴘᴋᴇ ʟɪʏᴇ!",
    "🍀 ʟᴜᴄᴋ ᴀᴀᴘᴋᴇ sᴀᴀᴛʜ ʜᴀɪ!",
    "🌺 ᴋᴀᴍᴀʟ ᴋɪ ᴛᴀʀᴀʜ ᴋʜɪʟᴏ!",
    "☘️ ʜᴀʀɪʏᴀᴀʟɪ ʜɪ ʜᴀʀɪʏᴀᴀʟɪ!",
    "🌿 sʜᴀᴀɴᴛɪ ʙᴀɴᴀʏᴇ ʀᴀᴋʜᴇɪɴ!",
    "🍂 ᴘᴀᴛᴊʜᴀᴅ ᴋᴀ ᴍᴀᴜsᴀᴍ!",
    "❄️ ᴛʜᴀɴᴅ ʟᴀɢ ʀᴀʜɪ ʜᴀɪ ᴋʏᴀ?",
    "☃️ sɴᴏᴡᴍᴀɴ ʙᴀɴᴀʏᴇɴɢᴇ ᴀᴀᴊ!",
    "🫶 ᴘʏᴀᴀʀ ʙᴀᴀɴᴛᴏ!",
    "😊 ʜᴀsᴛᴇ ʀᴀʜᴏ ᴍᴜsᴋᴜʀᴀᴛᴇ ʀᴀʜᴏ!",
    "🤗 ᴇᴋ ʙɪɢ ᴊʜᴀᴘᴘɪ!",
    "😎 sᴡᴀɢ sᴇ sᴡᴀɢᴀᴛ ʜᴀɪ!",
    "🥰 sᴀʙsᴇ ᴄᴜᴛᴇ ʟᴏɢ ʏᴀʜɪ ʜᴀɪ!",
    "💝 ʏᴇʜ ᴅɪʟ ᴛᴜᴍʜᴀʀᴇ ʟɪʏᴇ!",
    "🌼 ɢᴇɴᴅᴀ ᴘʜᴏᴏʟ ʙᴀɴ ɢᴀʏᴇ sᴀʙ!",
]


# ─────────────── Tagging Handler ───────────────

@app.on_message(
    (filters.command(["all", "tagall"]) | filters.regex(r"(?i)^@(all|tagall)\b"))
    & filters.group
    & ~filters.forwarded
    & ~filters.via_bot
)
async def tag_all_handler(client, message: Message):
    chat_id = message.chat.id

    # Admin / SUDO check
    if message.from_user and message.from_user.id not in SUDOERS:
        try:
            member = await client.get_chat_member(chat_id, message.from_user.id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await message.reply_text("» ᴏɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        except Exception:
            return await message.reply_text("» ғᴀɪʟᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ ᴀᴅᴍɪɴ sᴛᴀᴛᴜs.")

    # Prevent duplicate sessions in the same group
    if chat_id in _active_tag_sessions and _active_tag_sessions[chat_id]:
        return await message.reply_text(
            "» ᴛᴀɢɢɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!\n\n"
            "➻ ᴜsᴇ /cancel ᴛᴏ sᴛᴏᴘ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛᴀɢɢɪɴɢ."
        )

    # Determine mode: plain /all vs /all <text> vs /all reply
    custom_text = None
    reply_msg = None
    use_delay = False

    if message.reply_to_message:
        reply_msg = message.reply_to_message
        use_delay = True
    else:
        text_content = message.text or message.caption or ""
        text_content = text_content.strip()
        # If it was triggered as a command, message.command is populated
        if message.command:
            if len(message.command) > 1:
                custom_text = text_content.split(None, 1)[1]
                use_delay = True
        else:
            # If triggered via regex like @all, split manually
            words = text_content.split(None, 1)
            if len(words) > 1:
                custom_text = words[1]
                use_delay = True

    # Mark session as active
    _active_tag_sessions[chat_id] = True

    try:
        # Fetch all members
        members = []
        try:
            async for member in client.get_chat_members(chat_id):
                user = member.user
                # Skip bots, deleted accounts, the bot itself, and the assistant
                if user.is_bot or user.is_deleted:
                    continue
                if user.id in (BOT_ID, ASS_ID):
                    continue
                members.append(user)
        except ChatAdminRequired:
            _active_tag_sessions[chat_id] = False
            return await message.reply_text(
                "» ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ғᴇᴛᴄʜ ᴍᴇᴍʙᴇʀ ʟɪsᴛ!"
            )
        except Exception as e:
            _active_tag_sessions[chat_id] = False
            LOGGER.error(f"[TagAll] Failed to get members for {chat_id}: {e}")
            return await message.reply_text(
                f"» ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴍᴇᴍʙᴇʀs.\n\n**ᴇʀʀᴏʀ:** `{e}`"
            )

        if not members:
            _active_tag_sessions[chat_id] = False
            return await message.reply_text("» ɴᴏ ᴍᴇᴍʙᴇʀs ғᴏᴜɴᴅ ᴛᴏ ᴛᴀɢ!")

        # Shuffle members for randomness
        random.shuffle(members)

        # Prepare tag messages pool (shuffled)
        msg_pool = TAG_MESSAGES.copy()
        random.shuffle(msg_pool)
        msg_index = 0

        tagged = set()
        
        # Batch size logic: 1 if plain /all, 7-8 if text/reply is provided
        is_plain_all = not custom_text and not reply_msg
        batch_size = 1 if is_plain_all else random.randint(7, 8)
        
        total_members = len(members)
        total_tagged = 0

        # Send initial status
        status = await message.reply_text(
            f"» sᴛᴀʀᴛɪɴɢ ᴛᴀɢɢɪɴɢ {total_members} ᴍᴇᴍʙᴇʀs...\n"
            f"➻ ᴜsᴇ /cancel ᴛᴏ sᴛᴏᴘ ᴀɴʏᴛɪᴍᴇ."
        )

        # Process in batches
        for i in range(0, len(members), batch_size):
            # Check if cancelled
            if not _active_tag_sessions.get(chat_id, False):
                await client.send_message(
                    chat_id,
                    f"» ᴛᴀɢɢɪɴɢ ᴄᴀɴᴄᴇʟʟᴇᴅ!\n➻ ᴛᴀɢɢᴇᴅ {total_tagged}/{total_members} ᴍᴇᴍʙᴇʀs."
                )
                return

            batch = members[i:i + batch_size]
            mentions = []
            for user in batch:
                if user.id in tagged:
                    continue
                tagged.add(user.id)
                name = user.first_name or "User"
                # Truncate long names
                if len(name) > 15:
                    name = name[:15] + "..."
                mentions.append(f"[{name}](tg://user?id={user.id})")

            if not mentions:
                continue

            # Pick a tag message
            tag_msg = msg_pool[msg_index % len(msg_pool)]
            msg_index += 1

            # Build the final message
            mention_text = " ❃ ".join(mentions)
            if custom_text:
                text = f"**{custom_text}**\n\n{tag_msg}\n{mention_text}"
            elif reply_msg:
                text = f"{tag_msg}\n{mention_text}"
            else:
                text = f"{tag_msg}\n{mention_text}"

            try:
                if reply_msg:
                    await reply_msg.reply_text(text, disable_web_page_preview=True)
                else:
                    await client.send_message(
                        chat_id, text, disable_web_page_preview=True
                    )
                total_tagged += len(mentions)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    if reply_msg:
                        await reply_msg.reply_text(text, disable_web_page_preview=True)
                    else:
                        await client.send_message(
                            chat_id, text, disable_web_page_preview=True
                        )
                    total_tagged += len(mentions)
                except Exception:
                    pass
            except Exception as e:
                LOGGER.warning(f"[TagAll] Error sending tag batch in {chat_id}: {e}")
                continue

            # Apply delay between batches if custom text or reply
            if use_delay and (i + batch_size) < len(members):
                await asyncio.sleep(7)
            else:
                # Small delay even for plain /all to avoid flood
                await asyncio.sleep(1.5)

            # Randomize next batch size only if not plain /all
            if not is_plain_all:
                batch_size = random.randint(7, 8)

        # Done
        try:
            await status.delete()
        except Exception:
            pass

        await client.send_message(
            chat_id,
            f"✅ ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇ!\n➻ ᴛᴀɢɢᴇᴅ {total_tagged} ᴍᴇᴍʙᴇʀs sᴜᴄᴄᴇssғᴜʟʟʏ."
        )

    except Exception as e:
        LOGGER.error(f"[TagAll] Error in tag_all_handler: {e}")
        await message.reply_text(f"» sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ: `{e}`")
    finally:
        _active_tag_sessions[chat_id] = False


# ─────────────── Cancel Handler ───────────────

@app.on_message(
    filters.command(["cancel", "stoptag"])
    & filters.group
    & ~filters.forwarded
)
async def cancel_tagging(client, message: Message):
    chat_id = message.chat.id
    
    # Admin / SUDO check
    if message.from_user and message.from_user.id not in SUDOERS:
        try:
            member = await client.get_chat_member(chat_id, message.from_user.id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await message.reply_text("» ᴏɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        except Exception:
            return await message.reply_text("» ғᴀɪʟᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ ᴀᴅᴍɪɴ sᴛᴀᴛᴜs.")
    if chat_id in _active_tag_sessions and _active_tag_sessions[chat_id]:
        _active_tag_sessions[chat_id] = False
        await message.reply_text("» sᴛᴏᴘᴘɪɴɢ ᴛʜᴇ ᴛᴀɢɢɪɴɢ ᴏᴘᴇʀᴀᴛɪᴏɴ...")
    else:
        await message.reply_text("» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀɢɢɪɴɢ sᴇssɪᴏɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
