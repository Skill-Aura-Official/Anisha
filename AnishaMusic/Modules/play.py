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
import traceback

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from youtube_search import YoutubeSearch

from config import DURATION_LIMIT
from AnishaMusic import (
    ASS_ID,
    ASS_MENTION,
    ASS_NAME,
    ASS_USERNAME,
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    app,
    app2,
    anishadb,
    pytgcalls,
)
from AnishaMusic.Helpers.active import add_active_chat, is_active_chat, stream_on, currently_playing
from AnishaMusic.Helpers.downloaders import audio_dl, video_dl
from AnishaMusic.Helpers.errors import DurationLimitError
from AnishaMusic.Helpers.gets import get_file_name, get_url
from AnishaMusic.Helpers.inline import buttons
from AnishaMusic.Helpers.queue import put
from AnishaMusic.Helpers.thumbnails import gen_qthumb, gen_thumb
from AnishaMusic.Helpers.bass_db import get_bass_params
from AnishaMusic.Helpers.logger import log_activity
from AnishaMusic.Helpers.error_reporter import report_error

import traceback

def play_error_handler(func):
    async def wrapper(client, message):
        try:
            return await func(client, message)
        except Exception as e:
            LOGGER.error(f"Play command error: {e}\n{traceback.format_exc()}")
            try:
                await message.reply_text(f"» sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ\n\n**ᴇʀʀᴏʀ :** `{e}`")
            except:
                pass
            await report_error(
                module="play",
                error=e,
                chat_id=message.chat.id,
                chat_title=message.chat.title,
                user=message.from_user.first_name if message.from_user else "Unknown",
                extra_info=f"Command: {message.text[:100] if message.text else 'N/A'}",
            )
    return wrapper


@app.on_message(
    filters.command(["play", "vplay", "p"])
    & filters.group
    & ~filters.forwarded
    & ~filters.via_bot
)
@play_error_handler
async def play(_, message: Message):
    from AnishaMusic.Helpers.database import add_served_chat
    add_served_chat(message.chat.id)
    anisha = await message.reply_text("» ᴘʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...")
    try:
        await message.delete()
    except:
        pass

    try:
        try:
            get = await app.get_chat_member(message.chat.id, ASS_ID)
        except ChatAdminRequired:
            return await anisha.edit_text(
                f"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ғᴏʀ ɪɴᴠɪᴛɪɴɢ {BOT_NAME} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}."
            )
        if get.status == ChatMemberStatus.BANNED:
            unban_butt = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"ᴜɴʙᴀɴ {ASS_NAME}",
                            callback_data=f"unban_assistant {message.chat.id}|{ASS_ID}",
                        ),
                    ]
                ]
            )
            return await anisha.edit_text(
                text=f"» {BOT_NAME} ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ɪɴ {message.chat.title}\n\n𖢵 ɪᴅ : `{ASS_ID}`\n𖢵 ɴᴀᴍᴇ : {ASS_MENTION}\n𖢵 ᴜsᴇʀɴᴀᴍᴇ : @{ASS_USERNAME}\n\nᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴀɴᴅ ᴘʟᴀʏ ᴀɢᴀɪɴ...",
                reply_markup=unban_butt,
            )
    except UserNotParticipant:
        if message.chat.username:
            invitelink = message.chat.username
            try:
                await app2.resolve_peer(invitelink)
            except Exception as ex:
                LOGGER.error(ex)
        else:
            try:
                invitelink = await app.export_chat_invite_link(message.chat.id)
            except ChatAdminRequired:
                return await anisha.edit_text(
                    f"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ғᴏʀ ɪɴᴠɪᴛɪɴɢ {BOT_NAME} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}."
                )
            except Exception as ex:
                return await anisha.edit_text(
                    f"ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ {BOT_NAME} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
                )
        # Modern Pyrogram accepts both t.me/+ and t.me/joinchat/
        # Do not forcefully replace it, as it breaks newer hashes causing INVITE_HASH_EXPIRED
        anon = await anisha.edit_text(
            f"ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...\n\nɪɴᴠɪᴛɪɴɢ {ASS_NAME} ᴛᴏ {message.chat.title}."
        )
        try:
            await app2.join_chat(invitelink)
            await asyncio.sleep(2)
            await anisha.edit_text(
                f"{ASS_NAME} ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ,\n\nsᴛᴀʀᴛɪɴɢ sᴛʀᴇᴀᴍ..."
            )
        except UserAlreadyParticipant:
            pass
        except Exception as ex:
            return await anisha.edit_text(
                f"ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ {BOT_NAME} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
            )
        try:
            await app2.resolve_peer(invitelink)
        except:
            pass

    ruser = message.from_user.first_name
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice or message.reply_to_message.video)
        if message.reply_to_message
        else None
    )
    url = get_url(message)
    stream_type = "video" if message.command[0].lower() == "vplay" else "audio"

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"» sᴏʀʀʏ ʙᴀʙʏ, ᴛʀᴀᴄᴋ ʟᴏɴɢᴇʀ ᴛʜᴀɴ  {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʟᴀʏ ᴏɴ {BOT_NAME}."
            )

        file_name = get_file_name(audio)
        title = file_name
        duration = round(audio.duration / 60)
        file_path = (
            await message.reply_to_message.download(file_name)
            if not os.path.isfile(os.path.join("downloads", file_name))
            else f"downloads/{file_name}"
        )

    elif url:
        from AnishaMusic.Helpers.spotify import is_spotify_url, parse_spotify_url, get_spotify_track, get_spotify_playlist, get_spotify_album
        if is_spotify_url(url):
            details = parse_spotify_url(url)
            if not details:
                return await anisha.edit_text("» Invalid Spotify URL.")

            item_type = details["type"]
            item_id = details["id"]

            if item_type == "track":
                track = get_spotify_track(item_id)
                if not track:
                    return await anisha.edit_text("» Failed to retrieve Spotify track info.")

                try:
                    await anisha.edit_text("🔎")
                except:
                    pass
                try:
                    results = YoutubeSearch(track["query"], max_results=5).to_dict()
                except Exception as e:
                    LOGGER.error(f"Spotify Search Error: {e}\n{traceback.format_exc()}")
                    return await anisha.edit_text("» Failed to process Spotify track, try again...")

                if not results:
                    return await anisha.edit_text("» No YouTube match found for this Spotify track.")

                file_path = None
                last_error = None
                for result in results:
                    try:
                        url = f"https://youtube.com/watch?v={result['id']}"
                        title = result["title"]
                        videoid = result["id"]
                        duration = result.get("duration")
                        if not duration or duration == "0":
                            continue

                        secmul, dur, dur_arr = 1, 0, duration.split(":")
                        for i in range(len(dur_arr) - 1, -1, -1):
                            dur += int(dur_arr[i]) * secmul
                            secmul *= 60

                        if (dur / 60) > DURATION_LIMIT:
                            continue

                        file_path = await video_dl(url) if stream_type == "video" else await audio_dl(url)
                        if file_path:
                            break
                    except Exception as e:
                        LOGGER.warning(f"Spotify YT download failed for {result.get('id')}: {e}")
                        last_error = e
                        continue

                if not file_path:
                    error_msg = "» Failed to download Spotify track match from YouTube."
                    if last_error:
                        error_msg += f"\n\n**ʟᴀsᴛ ᴇʀʀᴏʀ:** `{last_error}`"
                    return await anisha.edit_text(error_msg)
            else:
                # Playlist or Album
                tracks = get_spotify_playlist(item_id) if item_type == "playlist" else get_spotify_album(item_id)
                if not tracks:
                    return await anisha.edit_text("» Failed to retrieve Spotify playlist/album tracks.")

                first_track = tracks[0]
                await anisha.edit_text(f"» Processing Spotify {item_type} ({len(tracks)} tracks)...")
                try:
                    results = YoutubeSearch(first_track["query"], max_results=5).to_dict()
                except Exception as e:
                    LOGGER.error(f"Spotify Playlist Error: {e}\n{traceback.format_exc()}")
                    return await anisha.edit_text("» Failed to process the first track of the playlist.")

                if not results:
                    return await anisha.edit_text("» No YouTube match found for the first track.")

                file_path = None
                last_error = None
                for result in results:
                    try:
                        url = f"https://youtube.com/watch?v={result['id']}"
                        title = result["title"]
                        videoid = result["id"]
                        duration = result.get("duration")
                        if not duration or duration == "0":
                            continue

                        secmul, dur, dur_arr = 1, 0, duration.split(":")
                        for i in range(len(dur_arr) - 1, -1, -1):
                            dur += int(dur_arr[i]) * secmul
                            secmul *= 60

                        if (dur / 60) > DURATION_LIMIT:
                            continue

                        file_path = await video_dl(url) if stream_type == "video" else await audio_dl(url)
                        if file_path:
                            break
                    except Exception as e:
                        LOGGER.warning(f"Playlist track download failed for {result.get('id')}: {e}")
                        last_error = e
                        continue

                if not file_path:
                    error_msg = "» Failed to download first track of Spotify playlist/album."
                    if last_error:
                        error_msg += f"\n\n**ʟᴀsᴛ ᴇʀʀᴏʀ:** `{last_error}`"
                    return await anisha.edit_text(error_msg)

                if await is_active_chat(message.chat.id):
                    await put(
                        message.chat.id,
                        title,
                        duration,
                        videoid,
                        file_path,
                        ruser,
                        message.from_user.id,
                        stream_type,
                    )
                else:
                    if stream_type == "video":
                        stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=get_bass_params(message.chat.id))
                    else:
                        stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=get_bass_params(message.chat.id))
                    try:
                        await pytgcalls.play(message.chat.id, stream)
                    except NoActiveGroupCall:
                        return await anisha.edit_text(
                            "**» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ғᴏᴜɴᴅ.**\n\nᴩʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
                        )
                    except Exception as e:
                        return await anisha.edit_text(
                            f"» sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ: {e}"
                        )
                    currently_playing[message.chat.id] = {
                        "title": title,
                        "duration": duration,
                        "file_path": file_path,
                        "videoid": videoid,
                        "req": ruser,
                        "user_id": message.from_user.id,
                        "stream_type": stream_type,
                    }
                    await stream_on(message.chat.id)
                    await add_active_chat(message.chat.id)
                    from AnishaMusic.Helpers.queue import preload_next_track
                    asyncio.create_task(preload_next_track(message.chat.id))

                for track in tracks[1:]:
                    mins = track["duration_sec"] // 60
                    secs = track["duration_sec"] % 60
                    dur_str = f"{mins}:{secs:02d}"
                    await put(
                        message.chat.id,
                        title=f"{track['title']} - {track['artist']}",
                        duration=dur_str,
                        videoid="spotify_unresolved",
                        file_path="downloads/spotify_unresolved.mp3",
                        ruser=ruser,
                        user_id=message.from_user.id,
                        stream_type=stream_type,
                    )

                imgt = await gen_thumb(videoid, message.from_user.id)
                total_added = len(tracks)
                await message.reply_photo(
                    photo=imgt,
                    caption=f"**➻ sᴛᴀʀᴛᴇᴅ sᴘᴏᴛɪғʏ {item_type.upper()}**\n\n‣ **ғɪʀsᴛ ᴛʀᴀᴄᴋ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴛᴏᴛᴀʟ ᴛʀᴀᴄᴋs :** `{total_added}`\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {ruser}",
                    reply_markup=buttons,
                )
                await log_activity(
                    "SPOTIFY",
                    f"Playing {item_type}: **{title}** ({total_added} tracks)",
                    chat_id=message.chat.id,
                    chat_title=message.chat.title,
                    user=ruser,
                )
                return await anisha.delete()
        else:
            try:
                results = YoutubeSearch(url, max_results=1).to_dict()
                title = results[0]["title"]
                duration = results[0]["duration"]
                videoid = results[0]["id"]

                secmul, dur, dur_arr = 1, 0, duration.split(":")
                for i in range(len(dur_arr) - 1, -1, -1):
                    dur += int(dur_arr[i]) * secmul
                    secmul *= 60
            except Exception as e:
                return await anisha.edit_text(f"sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ\n\n**ᴇʀʀᴏʀ :** `{e}`")

            if (dur / 60) > DURATION_LIMIT:
                return await anisha.edit_text(
                    f"» sᴏʀʀʏ ʙᴀʙʏ, ᴛʀᴀᴄᴋ ʟᴏɴɢᴇʀ ᴛʜᴀɴ  {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʟᴀʏ ᴏɴ {BOT_NAME}."
                )
            file_path = await video_dl(url) if stream_type == "video" else await audio_dl(url)

    else:
        if len(message.command) < 2:
            return await anisha.edit_text("» ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴɴᴀ ᴘʟᴀʏ ʙᴀʙʏ ?")
        try:
            await anisha.edit_text("🔎")
        except:
            pass
        query = message.text.split(None, 1)[1]
        try:
            results = YoutubeSearch(query, max_results=5).to_dict()
        except Exception as e:
            LOGGER.error(f"Query Search Error: {e}\n{traceback.format_exc()}")
            return await anisha.edit("» ғᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ǫᴜᴇʀʏ, ᴛʀʏ ᴘʟᴀʏɪɴɢ ᴀɢᴀɪɴ...")

        if not results:
            return await anisha.edit_text("» ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ, ᴛʀʏ ᴀ ᴅɪғғᴇʀᴇɴᴛ sᴇᴀʀᴄʜ.")

        file_path = None
        last_error = None
        for result in results:
            try:
                url = f"https://youtube.com/watch?v={result['id']}"
                title = result["title"]
                videoid = result["id"]
                duration = result.get("duration")
                if not duration or duration == "0":
                    continue

                secmul, dur, dur_arr = 1, 0, duration.split(":")
                for i in range(len(dur_arr) - 1, -1, -1):
                    dur += int(dur_arr[i]) * secmul
                    secmul *= 60

                if (dur / 60) > DURATION_LIMIT:
                    continue

                file_path = await video_dl(url) if stream_type == "video" else await audio_dl(url)
                if file_path:
                    break
            except Exception as e:
                LOGGER.warning(f"Download failed for query search result {result.get('id')}: {e}")
                last_error = e
                continue

        if not file_path:
            error_msg = "» ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ/ᴘʟᴀʏ ᴀɴʏ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs."
            if last_error:
                error_msg += f"\n\n**ʟᴀsᴛ ᴇʀʀᴏʀ:** `{last_error}`"
            return await anisha.edit_text(error_msg)

    # Ensure videoid is defined (for Telegram audio files it won't be)
    try:
        videoid
    except NameError:
        videoid = "telegram_audio"

    if await is_active_chat(message.chat.id):
        await put(
            message.chat.id,
            title,
            duration,
            videoid,
            file_path,
            ruser,
            message.from_user.id,
            stream_type,
        )
        position = len(anishadb.get(message.chat.id))
        qimg = await gen_qthumb(videoid, message.from_user.id)
        await message.reply_photo(
            photo=qimg,
            caption=f"**➻ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ ᴀᴛ {position}**\n\n‣ **ᴛɪᴛʟᴇ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}` ᴍɪɴᴜᴛᴇs\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {ruser}",
            reply_markup=buttons,
        )
        await log_activity(
            "QUEUE",
            f"Added to queue #{position}: **{title}** (`{duration}`)",
            chat_id=message.chat.id,
            chat_title=message.chat.title,
            user=ruser,
        )
    else:
        if stream_type == "video":
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.SD_480p, video_flags=MediaStream.Flags.AUTO_DETECT, ffmpeg_parameters=get_bass_params(message.chat.id))
        else:
            stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=get_bass_params(message.chat.id))
        try:
            await pytgcalls.play(message.chat.id, stream)
        except NoActiveGroupCall:
            return await anisha.edit_text(
                "**» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ғᴏᴜɴᴅ.**\n\nᴩʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
            )
        except Exception as e:
            return await anisha.edit_text(
                f"» sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ: {e}"
            )

        currently_playing[message.chat.id] = {
            "title": title,
            "duration": duration,
            "file_path": file_path,
            "videoid": videoid,
            "req": ruser,
            "user_id": message.from_user.id,
            "stream_type": stream_type,
        }
        await stream_on(message.chat.id)
        await add_active_chat(message.chat.id)
        from AnishaMusic.Helpers.queue import preload_next_track
        asyncio.create_task(preload_next_track(message.chat.id))

        await log_activity(
            "PLAY",
            f"Started streaming: **{title}** (`{duration}`) [{stream_type}]",
            chat_id=message.chat.id,
            chat_title=message.chat.title,
            user=ruser,
        )

        async def send_play_msg():
            imgt = await gen_thumb(videoid, message.from_user.id)
            await message.reply_photo(
                photo=imgt,
                caption=f"**➻ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ**\n\n‣ **ᴛɪᴛʟᴇ :** [{title[:27]}](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n‣ **ᴅᴜʀᴀᴛɪᴏɴ :** `{duration}` ᴍɪɴᴜᴛᴇs\n‣ **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {ruser}",
                reply_markup=buttons,
            )
            await anisha.delete()

        asyncio.create_task(send_play_msg())
        return
