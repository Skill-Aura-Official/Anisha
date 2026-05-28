from os import getenv

from dotenv import load_dotenv

load_dotenv()


API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")

BOT_TOKEN = getenv("BOT_TOKEN", None)
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "300"))

OWNER_ID = int(getenv("OWNER_ID"))

PING_IMG = getenv("PING_IMG", "https://res.cloudinary.com/dwadwpalt/image/upload/v1779568440/b2bc927b-4237-4782-95c7-7645eddd7a5b_odpu9y.png")
START_IMG = getenv("START_IMG", "https://res.cloudinary.com/dwadwpalt/image/upload/v1779568704/93e15cb3-467f-4da7-a409-132d077182ee_w1whxh.png")

SESSION = getenv("SESSION", None)

SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/TSB_Council_Support")
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/TSB_Bots")

SUDO_USERS = list(map(int, getenv("SUDO_USERS", "2067003147").split()))


SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

LOG_CHANNEL_ID = int(getenv("LOG_CHANNEL_ID", "-1003928121906"))

FAILED = getenv("FAILED_IMG", "https://res.cloudinary.com/dwadwpalt/image/upload/v1779570850/93a7fe04-59e8-422b-b86d-ed6b8f32805a_izdyye.png")
