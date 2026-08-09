import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "wh-secret-path")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}" if BASE_URL else ""

WEBAPP_URL = f"{BASE_URL}/app" if BASE_URL else ""

DB_PATH = os.getenv("DB_PATH", "codelingo.db")

PREMIUM_PRICE_STARS = int(os.getenv("PREMIUM_PRICE_STARS", "150"))
PREMIUM_DURATION_DAYS = int(os.getenv("PREMIUM_DURATION_DAYS", "30"))

DEFAULT_HP = 5
