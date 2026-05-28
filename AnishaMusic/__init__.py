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
import logging
import os
import time

# Add the project root to PATH so yt-dlp and py-tgcalls can find ffmpeg.exe
os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.pathsep + os.environ.get("PATH", "")

from pyrogram import Client, filters

# Monkeypatch GroupcallForbidden for py-tgcalls compatibility
import pyrogram.errors
class GroupcallForbidden(pyrogram.errors.Forbidden):
    pass
pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pytgcalls import PyTgCalls

import config

StartTime = time.time()

import sys

_stream_handler = logging.StreamHandler(
    stream=open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
)

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("anishalogs.txt", encoding="utf-8"), _stream_handler],
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.DEBUG)
LOGGER = logging.getLogger("AnishaMusic")

app = Client(
    "AnishaMusic",
    config.API_ID,
    config.API_HASH,
    bot_token=config.BOT_TOKEN,
    in_memory=True,
    max_concurrent_transmissions=3,
)

app2 = Client(
    "TSBCouncil",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=str(config.SESSION),
    in_memory=True,
)

pytgcalls = PyTgCalls(app2)

SUDOERS = filters.user()
MANAGERS = set()
GBANNED_USERS = set()
SUNAME = config.SUPPORT_CHAT.split("me/")[1]

BOT_ID = 0
BOT_NAME = ""
BOT_USERNAME = ""
BOT_MENTION = ""
ASS_ID = 0
ASS_NAME = ""
ASS_USERNAME = ""
ASS_MENTION = ""
anishadb = {}


async def anisha_startup():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    LOGGER.info(
        "\n\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃★ ANISHA MUSIC BOT ★\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    )
    global BOT_ID, BOT_NAME, BOT_USERNAME, BOT_MENTION, anishadb
    global ASS_ID, ASS_NAME, ASS_USERNAME, ASS_MENTION, SUDOERS

    await app.start()
    LOGGER.info("[•] Booting Anisha Music Bot...")

    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_NAME = getme.first_name
    BOT_USERNAME = getme.username
    BOT_MENTION = getme.mention

    await app2.start()
    LOGGER.info("[•] Booting Anisha Music Assistant...")

    getme2 = await app2.get_me()
    ASS_ID = getme2.id
    ASS_NAME = getme2.first_name + " " + (getme2.last_name or "")
    ASS_USERNAME = getme2.username
    ASS_MENTION = getme2.mention
    for chat in ["TSB_Council", "TSB_Bots", "TSB_Council_Support"]:
        try:
            await app2.join_chat(chat)
        except:
            pass

    # Load databases
    from AnishaMusic.Helpers.database import load_db
    db = load_db()
    for uid in db["cofounders"]:
        SUDOERS.add(uid)
    for uid in db["managers"]:
        MANAGERS.add(uid)
    for uid in db["gbanned"]:
        GBANNED_USERS.add(uid)

    for SUDOER in config.SUDO_USERS:
        SUDOERS.add(SUDOER)
    if config.OWNER_ID not in config.SUDO_USERS:
        SUDOERS.add(config.OWNER_ID)

    LOGGER.info("[•] Local Database Initialized...")
    LOGGER.info("[•] Anisha Music Clients Booted Successfully.")


asyncio.get_event_loop().run_until_complete(anisha_startup())
