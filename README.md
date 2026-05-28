# 🎵 Anisha Music Bot

![Anisha Music Bot](bot_avatar.png)

Anisha Music Bot is a premium, high-performance Telegram music bot designed to stream high-quality audio and video directly into group video chats. Powered by Pyrogram and PyTgCalls.

---

## ✨ Key Features

- **High-Quality Streaming**: Streams low-latency audio and 480p/720p video.
- **Dynamic Queue Management**: Preloads next tracks dynamically in the background for gapless playback.
- **Custom Audio Filters**: Adjust bass level controls, audio presets, and playback speeds on-the-fly.
- **Sudo Control Suite**: Advanced sudo command modules (e.g. Broadcasts, Global Bans, Sudo Management, Eval, Leave-all).
- **Interactive Inline Buttons**: Easily pause, resume, skip, or end streams using interactive panels.
- **Smart Auto-Leave**: The assistant account automatically leaves voice chats if no audio is playing for over an hour to conserve resources.
- **TagAll Module**: Tag group members dynamically when needed.

---

## 🚀 What's New?

1. **Daily Auto-Restart (5:30 AM IST / 00:00 UTC)**
   - Implemented an internal background watchdog that gracefully shuts down and reboots the bot process every day at 5:30 AM IST (00:00 UTC) to keep memory usage minimal.
2. **Direct-to-Owner DM Error Reporter**
   - Automatically catches exceptions in critical modules (`play`, `watcher`, `callback`, `skip`) and forwards detailed tracebacks directly to the bot owner's DM (rate-limited to avoid spam).
3. **Advanced Database Stats Tracking**
   - Tracks the number of unique user direct messages (`/start` in PM) and served groups (`/play` and `/start` in groups) in a lightweight local JSON database. Use `/stats` or `/sysstats` to view counters.
4. **Resilient Video Cache Handling**
   - Smart caching in the download helper distinguishes between audio (.opus) and video (.mp4) files, ensuring `/vplay` always streams visual video elements and doesn't get blocked by cached audio tracks.
5. **Crash-Loop Protective Startup Script**
   - A robust runner script (`anisha`) runs a cleanup process on boot (clearing temp files and rotating log files) and features a protective cooldown (5 minutes) if the bot experiences rapid crash loops.

---

## 🛠️ Installation & Local Run

### Prerequisites
* Python 3.9 or higher
* FFmpeg installed and added to system path (or placed in the project root directory)

### Steps
1. **Clone the repository and enter the directory**:
   ```bash
   cd "Music Bot"
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and fill in your credentials:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   SESSION_NAME=your_assistant_session_string
   OWNER_ID=your_telegram_user_id
   LOG_CHANNEL_ID=your_log_channel_id
   ```
4. **Run the bot**:
   Using the crash-protective runner script (Linux/macOS):
   ```bash
   bash anisha
   ```
   Or run the Python module directly:
   ```bash
   python -m AnishaMusic
   ```

---

## 🚢 Deployment

### 🐳 Docker Deployment
Build and run the container locally:
```bash
docker build -t anisha-music .
docker run -d --name anisha-bot --env-file .env anisha-music
```

### 💜 Heroku Deployment
The project contains `heroku.yml` and `Procfile` configured to use the `anisha` bash runner script.
1. Create a new App on Heroku.
2. Connect your Git repository.
3. Add the following buildpacks:
   - `heroku/python`
   - `https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git` (to support audio/video transcoding)
4. Set up your config vars matching the `.env` schema.
5. Deploy the branch. Heroku will automatically launch the worker dyno using `bash anisha`.

---

## 📜 User & Admin Commands

### Sudo & Owner Commands
- `/stats` or `/sysstats` - Show system, activity, and database stats.
- `/restart` - Manually trigger a clean reboot.
- `/broadcast [message]` - Broadcast a message to all chats.
- `/addsudo` & `/delsudo` - Manage sudo privileges.
- `/gban` & `/ungban` - Globally ban/unban users from using the bot.
- `/eval [expression]` - Run a python script evaluation code.
- `/leaveall` - Command assistant to leave all chats.

### Play & Stream Control Commands
- `/play [song name/link]` - Search and stream audio.
- `/vplay [song name/link]` - Search and stream video.
- `/pause` - Pause the active stream.
- `/resume` - Resume the paused stream.
- `/skip` or `/next` - Skip current track to the next queued item.
- `/stop` or `/end` - Stop the active stream and clear the queue.
- `/queue` - Show currently queued tracks.
