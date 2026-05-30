# MIT License
# Copyright (c) 2026 The Sovereign Brotherhood

import asyncio
import logging
import os
from yt_dlp import YoutubeDL

LOGGER = logging.getLogger("AnishaMusic")

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_common_opts = {
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
    "ffmpeg_location": _project_root,
    "noplaylist": True,
    "extractor_retries": 3,
    "retries": 3,
    "socket_timeout": 30,
}

ydl_opts = {
    **_common_opts,
    "format": "bestaudio[acodec=opus]/bestaudio[ext=m4a]/bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "opus",
        "preferredquality": "192",
    }],
}
ydl = YoutubeDL(ydl_opts)

video_opts = {
    **_common_opts,
    "format": "best[height<=720]",
}
v_ydl = YoutubeDL(video_opts)


def _audio_dl(url: str) -> str:
    import glob
    LOGGER.info(f"[Downloader] Audio download: {url}")
    try:
        sin = ydl.extract_info(url, False)
        vid_id = sin['id']
        existing = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        if existing:
            LOGGER.info(f"[Downloader] Cached: {existing[0]}")
            return existing[0]
        ydl.download([url])
        downloaded = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        if downloaded:
            return downloaded[0]
        return os.path.join("downloads", f"{vid_id}.{sin.get('ext', 'webm')}")
    except Exception as e:
        LOGGER.error(f"[Downloader] Audio FAILED: {e}")
        raise


async def audio_dl(url: str) -> str:
    return await asyncio.to_thread(_audio_dl, url)


def _video_dl(url: str) -> str:
    import glob
    LOGGER.info(f"[Downloader] Video download: {url}")
    try:
        sin = v_ydl.extract_info(url, False)
        vid_id = sin['id']
        existing = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        for f in existing:
            if not f.endswith(('.opus', '.mp3', '.m4a')):
                return f
        v_ydl.download([url])
        downloaded = glob.glob(os.path.join("downloads", f"{vid_id}.*"))
        for f in downloaded:
            if not f.endswith(('.opus', '.mp3', '.m4a')):
                return f
        return os.path.join("downloads", f"{vid_id}.{sin.get('ext', 'mp4')}")
    except Exception as e:
        LOGGER.error(f"[Downloader] Video FAILED: {e}")
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
            LOGGER.error(f"[Downloader] On-demand failed: {e}")
            return None, None

    try:
        results = YoutubeSearch(title, max_results=5).to_dict()
    except Exception as e:
        LOGGER.error(f"[Downloader] Search failed: {e}")
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
            LOGGER.warning(f"[Downloader] Result {result.get('id')} failed: {e}")
            continue

    return None, None


async def resolve_and_download(title: str, videoid: str, stream_type: str):
    return await asyncio.to_thread(_resolve_and_download, title, videoid, stream_type)


async def saavn_or_youtube(url: str, title: str = "", videoid: str = "", stream_type: str = "audio") -> str:
    """Download audio from YouTube."""
    LOGGER.info(f"[Downloader] Downloading: {title or url}")
    return await audio_dl(url)
