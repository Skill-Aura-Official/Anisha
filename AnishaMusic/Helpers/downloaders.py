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

from yt_dlp import YoutubeDL

LOGGER = logging.getLogger("AnishaMusic")

# Resolve the project root (where ffmpeg.exe lives)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Common options shared between audio and video
_common_opts = {
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
    "ffmpeg_location": _project_root,
    "noplaylist": True,
    "extractor_retries": 3,
    "cookiefile": "/home/MusicBot/cookies.txt",
    "retries": 3,
    "socket_timeout": 15,
}

ydl_opts = {
    **_common_opts,
    # Prefer highest quality opus/m4a audio for better clarity and bass
    "format": "bestaudio[acodec=opus]/bestaudio[ext=m4a]/bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "opus",
        "preferredquality": "320",
    }],
}
ydl = YoutubeDL(ydl_opts)


def _audio_dl(url: str) -> str:
    import glob
    LOGGER.info(f"[Downloader] Starting audio download: {url}")
    try:
        sin = ydl.extract_info(url, False)
        vid_id = sin['id']

        # Check if file already exists in downloads matching this video ID (e.g. mp3, webm, m4a, opus)
        existing = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        if existing:
            LOGGER.info(f"[Downloader] File already cached: {existing[0]}")
            return existing[0]

        ydl.download([url])

        # Find the downloaded file
        downloaded = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        if downloaded:
            LOGGER.info(f"[Downloader] Audio download complete: {downloaded[0]}")
            return downloaded[0]

        # Fallback if somehow not found
        fallback = os.path.join("downloads", f"{vid_id}.{sin.get('ext', 'webm')}")
        LOGGER.info(f"[Downloader] Audio download complete (fallback path): {fallback}")
        return fallback
    except Exception as e:
        LOGGER.error(f"[Downloader] Audio download FAILED: {e}")
        raise


async def audio_dl(url: str) -> str:
    return await asyncio.to_thread(_audio_dl, url)


video_opts = {
    **_common_opts,
    "format": "best[height<=720]",
}
v_ydl = YoutubeDL(video_opts)


def _video_dl(url: str) -> str:
    import glob
    LOGGER.info(f"[Downloader] Starting video download: {url}")
    try:
        sin = v_ydl.extract_info(url, False)
        vid_id = sin['id']

        # Look specifically for video formats, not opus audio
        existing = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        for ext_path in existing:
            if not ext_path.endswith(('.opus', '.mp3', '.m4a')):
                LOGGER.info(f"[Downloader] Video file already cached: {ext_path}")
                return ext_path

        v_ydl.download([url])

        downloaded = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        for ext_path in downloaded:
            if not ext_path.endswith(('.opus', '.mp3', '.m4a')):
                LOGGER.info(f"[Downloader] Video download complete: {ext_path}")
                return ext_path

        fallback = os.path.join("downloads", f"{vid_id}.{sin.get('ext', 'mp4')}")
        LOGGER.info(f"[Downloader] Video download complete (fallback path): {fallback}")
        return fallback
    except Exception as e:
        LOGGER.error(f"[Downloader] Video download FAILED: {e}")
        raise


async def video_dl(url: str) -> str:
    return await asyncio.to_thread(_video_dl, url)


def _resolve_and_download(title: str, videoid: str, stream_type: str):
    from youtube_search import YoutubeSearch
    if len(videoid) == 11:
        url = f"https://youtube.com/watch?v={videoid}"
        try:
            file_path = _video_dl(url) if stream_type == "video" else _audio_dl(url)
            return file_path, videoid
        except Exception as e:
            print(f"Error downloading on demand for {url}: {e}")
            return None, None

    # Query search fallback loop
    try:
        results = YoutubeSearch(title, max_results=5).to_dict()
    except Exception as e:
        print(f"Error searching on demand for {title}: {e}")
        return None, None

    if not results:
        return None, None

    for result in results:
        try:
            duration_str = result.get("duration")
            if not duration_str or duration_str == "0":
                continue

            secmul, dur, dur_arr = 1, 0, duration_str.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            import config
            if (dur / 60) > config.DURATION_LIMIT:
                continue

            v_id = result["id"]
            url = f"https://youtube.com/watch?v={v_id}"
            file_path = _video_dl(url) if stream_type == "video" else _audio_dl(url)
            if file_path:
                return file_path, v_id
        except Exception as e:
            print(f"On-demand download failed for result {result.get('id')}: {e}")
            continue

    return None, None


async def resolve_and_download(title: str, videoid: str, stream_type: str):
    return await asyncio.to_thread(_resolve_and_download, title, videoid, stream_type)

async def saavn_or_youtube(query: str, videoid: str = "", stream_type: str = "audio") -> str:
    """Try JioSaavn first, fall back to YouTube if it fails."""
    from AnishaMusic.Helpers.saavn import saavn_download
    try:
        LOGGER.info(f"[Downloader] Trying JioSaavn for: {query}")
        return await saavn_download(query)
    except Exception as e:
        LOGGER.warning(f"[Downloader] JioSaavn failed: {e}, falling back to YouTube")
        if videoid and len(videoid) == 11:
            url = f"https://youtube.com/watch?v={videoid}"
            return await audio_dl(url)
        raise Exception(f"Both JioSaavn and YouTube failed for: {query}")
