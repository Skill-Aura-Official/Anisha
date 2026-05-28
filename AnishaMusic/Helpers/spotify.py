import json
import re
import urllib.request
from typing import Dict, List, Optional

import config

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    HAS_SPOTIPY = True
except ImportError:
    HAS_SPOTIPY = False

# Global client
sp = None


def init_spotify():
    global sp
    if sp is not None:
        return sp

    if not HAS_SPOTIPY:
        return None

    cid = getattr(config, "SPOTIFY_CLIENT_ID", None)
    csecret = getattr(config, "SPOTIFY_CLIENT_SECRET", None)
    if not cid or not csecret:
        return None
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=cid,
            client_secret=csecret,
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        sp.search(q="test", limit=1, type="track")
        return sp
    except Exception:
        sp = None
        return None


def is_spotify_url(url: str) -> bool:
    return "open.spotify.com" in url


def parse_spotify_url(url: str) -> Dict:
    url = url.split("?")[0]
    parts = url.split("/")
    if len(parts) < 5:
        return {}
    item_type = parts[-2]
    item_id = parts[-1]
    if item_type in ["track", "playlist", "album"]:
        return {"type": item_type, "id": item_id}
    return {}


def _oembed_get_name(spotify_url: str) -> Optional[str]:
    """Use Spotify's public oEmbed API to get the track/album/playlist title.
    No authentication required."""
    try:
        api_url = f"https://open.spotify.com/oembed?url={spotify_url}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode("utf-8"))
        title = data.get("title", "")
        if title:
            return title
    except Exception:
        pass
    return None


def get_spotify_track(track_id: str) -> Optional[Dict]:
    try:
        url = f"https://open.spotify.com/embed/track/{track_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if match:
            data = json.loads(match.group(1))
            entity = data['props']['pageProps']['state']['data']['entity']
            title = entity.get("title", entity.get("name", ""))
            artist = entity.get("subtitle", "")
            return {
                "title": title,
                "artist": artist,
                "duration_sec": 0,
                "query": f"{title} {artist} audio".strip()
            }
    except Exception:
        pass

    # Fallback: oEmbed API (no auth needed)
    name = _oembed_get_name(f"https://open.spotify.com/track/{track_id}")
    if name:
        return {
            "title": name,
            "artist": "",
            "duration_sec": 0,
            "query": name,
        }
    return None


def get_spotify_playlist(playlist_id: str) -> Optional[List[Dict]]:
    try:
        url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if match:
            data = json.loads(match.group(1))
            entity = data['props']['pageProps']['state']['data']['entity']
            tracks = []
            if 'trackList' in entity:
                for item in entity['trackList']:
                    title = item.get("title", item.get("name", ""))
                    artist = item.get("subtitle", "")
                    tracks.append({
                        "title": title,
                        "artist": artist,
                        "duration_sec": 0,
                        "query": f"{title} {artist} audio".strip()
                    })
            elif 'tracks' in entity:
                for item in entity['tracks']['items']:
                    track = item.get("track", {})
                    if not track: continue
                    title = track.get("name", "")
                    artist = track["artists"][0]["name"] if track.get("artists") else ""
                    duration_sec = int(track.get("duration_ms", 0) / 1000)
                    tracks.append({
                        "title": title,
                        "artist": artist,
                        "duration_sec": duration_sec,
                        "query": f"{title} {artist} audio".strip()
                    })
            if tracks:
                return tracks
    except Exception:
        pass

    # Fallback: get playlist name via oEmbed, play as single search
    name = _oembed_get_name(
        f"https://open.spotify.com/playlist/{playlist_id}"
    )
    if name:
        return [{"title": name, "artist": "", "duration_sec": 0, "query": name}]
    return None


def get_spotify_album(album_id: str) -> Optional[List[Dict]]:
    try:
        url = f"https://open.spotify.com/embed/album/{album_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8")
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if match:
            data = json.loads(match.group(1))
            entity = data['props']['pageProps']['state']['data']['entity']
            tracks = []
            if 'trackList' in entity:
                for item in entity['trackList']:
                    title = item.get("title", item.get("name", ""))
                    artist = item.get("subtitle", "")
                    tracks.append({
                        "title": title,
                        "artist": artist,
                        "duration_sec": 0,
                        "query": f"{title} {artist} audio".strip()
                    })
            if tracks:
                return tracks
    except Exception:
        pass

    # Fallback: get album name via oEmbed
    name = _oembed_get_name(f"https://open.spotify.com/album/{album_id}")
    if name:
        return [{"title": name, "artist": "", "duration_sec": 0, "query": name}]
    return None
