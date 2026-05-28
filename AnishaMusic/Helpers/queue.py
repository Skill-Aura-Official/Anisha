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
import os
import logging
from AnishaMusic import anishadb

LOGGER = logging.getLogger("AnishaMusic")
_preload_tasks = {}

async def preload_next_track(chat_id: int):
    # If already preloading for this chat, skip
    if chat_id in _preload_tasks and not _preload_tasks[chat_id].done():
        return

    get = anishadb.get(chat_id)
    if not get or len(get) == 0:
        return

    next_track = get[0]
    file_path = next_track.get("file_path")
    videoid = next_track.get("videoid")
    
    # If file already exists and is not unresolved, no need to download
    if file_path and os.path.exists(file_path) and "unresolved" not in file_path:
        return

    async def worker():
        try:
            title = next_track["title"]
            stream_type = next_track.get("stream_type", "audio")
            LOGGER.info(f"[Preload] Starting background preload for {title} in chat {chat_id}")
            
            from AnishaMusic.Helpers.downloaders import resolve_and_download
            new_file, new_id = await resolve_and_download(title, videoid, stream_type)
            
            if new_file and os.path.exists(new_file):
                # Update the queue item in-place
                current_queue = anishadb.get(chat_id)
                if current_queue and len(current_queue) > 0 and current_queue[0]["title"] == title:
                    current_queue[0]["file_path"] = new_file
                    current_queue[0]["videoid"] = new_id
                    LOGGER.info(f"[Preload] Successfully preloaded/resolved: {new_file}")
            else:
                LOGGER.warning(f"[Preload] Preload failed to resolve/download: {title}")
        except Exception as e:
            LOGGER.error(f"[Preload] Error preloading next track: {e}")

    _preload_tasks[chat_id] = asyncio.create_task(worker())


async def put(
    chat_id,
    title,
    duration,
    videoid,
    file_path,
    ruser,
    user_id,
    stream_type="audio",
):
    put_f = {
        "title": title,
        "duration": duration,
        "file_path": file_path,
        "videoid": videoid,
        "req": ruser,
        "user_id": user_id,
        "stream_type": stream_type,
    }
    get = anishadb.get(chat_id)
    if get:
        anishadb[chat_id].append(put_f)
    else:
        anishadb[chat_id] = []
        anishadb[chat_id].append(put_f)

    # Trigger preloading the next song in the background
    asyncio.create_task(preload_next_track(chat_id))

