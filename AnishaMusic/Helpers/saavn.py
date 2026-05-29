import os
import asyncio
import logging
import requests
import base64
from Crypto.Cipher import DES

LOGGER = logging.getLogger("AnishaMusic")

def decrypt_url(encrypted_url: str) -> str:
    key = b'38346591'
    cipher = DES.new(key, DES.MODE_ECB)
    enc = base64.b64decode(encrypted_url.strip().encode())
    dec = cipher.decrypt(enc)
    # Remove PKCS5 padding bytes
    url = dec.decode('utf-8', errors='ignore')
    url = url.rstrip('\x00\x01\x02\x03\x04\x05\x06\x07\x08').strip()
    return url.replace('_96.mp4', '_320.mp4')

def search_saavn(query: str) -> dict:
    try:
        r = requests.get(
            'https://www.jiosaavn.com/api.php',
            params={
                '__call': 'search.getResults',
                'q': query,
                'p': 1,
                'n': 1,
                '_format': 'json',
                '_marker': 0,
                'ctx': 'web6dot0'
            },
            timeout=10
        )
        results = r.json().get('results', [])
        if not results:
            return None
        return results[0]
    except Exception as e:
        LOGGER.error(f"[Saavn] Search failed: {e}")
        return None

def get_saavn_url(song_id: str) -> str:
    try:
        r = requests.get(
            'https://www.jiosaavn.com/api.php',
            params={
                '__call': 'song.getDetails',
                'cc': 'in',
                '_marker': '0',
                '_format': 'json',
                'pids': song_id
            },
            timeout=10
        )
        data = r.json().get(song_id, {})
        encrypted = data.get('encrypted_media_url')
        if not encrypted:
            return None
        return decrypt_url(encrypted)
    except Exception as e:
        LOGGER.error(f"[Saavn] Get URL failed: {e}")
        return None

def _download_saavn(query: str) -> str:
    LOGGER.info(f"[Saavn] Searching: {query}")
    song = search_saavn(query)
    if not song:
        raise Exception("No results found on JioSaavn")

    song_id = song['id']
    title = song.get('song', query)
    url = get_saavn_url(song_id)
    if not url:
        raise Exception("Could not get download URL from JioSaavn")

    os.makedirs('downloads', exist_ok=True)
    file_path = f"downloads/saavn_{song_id}.m4a"

    if os.path.exists(file_path):
        LOGGER.info(f"[Saavn] Cached: {file_path}")
        return file_path

    LOGGER.info(f"[Saavn] Downloading: {title}")
    r = requests.get(url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    f_size = os.path.getsize(file_path)
    if f_size < 10000:
        os.remove(file_path)
        raise Exception(f"Downloaded file too small: {f_size} bytes")

    # Convert to opus for pytgcalls compatibility
    opus_path = file_path.replace('.m4a', '.opus')
    import subprocess
    result = subprocess.run(
        ['ffmpeg', '-i', file_path, '-c:a', 'libopus', '-b:a', '128k', opus_path, '-y'],
        capture_output=True, text=True
    )
    if result.returncode == 0 and os.path.exists(opus_path):
        os.remove(file_path)
        file_path = opus_path
        LOGGER.info(f"[Saavn] Converted to opus: {file_path}")
    else:
        LOGGER.warning(f"[Saavn] Opus conversion failed, using m4a: {result.stderr[-200:]}")

    LOGGER.info(f"[Saavn] Downloaded: {file_path}")
    return file_path

async def saavn_download(query: str) -> str:
    return await asyncio.to_thread(_download_saavn, query)
