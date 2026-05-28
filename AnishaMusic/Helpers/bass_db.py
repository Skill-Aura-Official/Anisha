chat_bass_db = {}
chat_preset_db = {}

# Default audio enhancement: dynamic normalization to make quiet audio louder,
# keep volume consistently full, and prevent digital clipping/cracking.
_DEFAULT_AUDIO_FILTER = "dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress=3"


def get_bass_params(chat_id: int) -> str:
    preset = chat_preset_db.get(chat_id, "bass")
    level = chat_bass_db.get(chat_id, 0)  # Default bass is 0 (no boost)

    if preset == "jazz":
        # 3dB bass boost, 1.5dB treble to stay warm but clear, compress=4.5 to keep vocals loud
        filters = "bass=g=3,treble=g=1.5,dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress=4.5"
    elif preset == "clean":
        # Pure dynamic normalizer with no bass boost
        filters = "dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress=3"
    elif preset == "heavy":
        # 8dB heavy bass boost, 2dB treble to keep vocals crisp, compress=7 to dynamically balance vocals
        filters = "bass=g=8,treble=g=2.0,equalizer=f=80:width_type=h:width=50:g=2,dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress=7"
    elif preset == "vocal":
        # Decreased bass, boosted vocals mid-range, compress=3
        filters = "bass=g=-2,treble=g=2.0,equalizer=f=3000:width_type=h:width=500:g=2,dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress=3"
    else:  # "bass" preset (default)
        if level <= 0:
            filters = "dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress=3"
        else:
            # Map user's 0-100 level smoothly to 0-8dB gain
            safe_level = max(1.0, min(8.0, level * 0.08))
            # Automatically scale the compress factor based on bass boost level (range: 3.5 to 7.0)
            # This dynamically boosts vocals to make sure they are never squashed by heavy bass
            comp_val = 3.0 + (safe_level * 0.5)
            # Treble boost (range: 0.2 to 1.6dB) to preserve vocal clarity
            treb_val = safe_level * 0.2
            filters = f"bass=g={safe_level:.1f},treble=g={treb_val:.1f},dynaudnorm=f=150:g=15:peak=0.95:maxgain=15:compress={comp_val:.1f}"

    return f"--audio ---mid -af {filters}"


def get_bass_seek_params(chat_id: int, seconds: int) -> str:
    bass_params = get_bass_params(chat_id)
    return f"-ss {seconds} {bass_params}"


def set_bass(chat_id: int, level: int):
    chat_bass_db[chat_id] = level
