import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("توکن ربات معتبر نیست! لطفاً آن را در فایل .env وارد کنید.")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

    ZARINPAL_API_KEY = os.getenv("ZARINPAL_API_KEY", "your_zarinpal_api_key_here")
    IDPAY_API_KEY = os.getenv("IDPAY_API_KEY", "your_idpay_api_key_here")

    ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "")
    if ADMIN_USER_IDS:
        ADMIN_USER_IDS = [int(uid.strip()) for uid in ADMIN_USER_IDS.split(",") if uid.strip().isdigit()]
    else:
        ADMIN_USER_IDS = []

    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

    return {
        "token": BOT_TOKEN,
        "database_url": DATABASE_URL,
        "zarinpal_api_key": ZARINPAL_API_KEY,
        "idpay_api_key": IDPAY_API_KEY,
        "admin_user_ids": ADMIN_USER_IDS,
        "logging_level": LOGGING_LEVEL
    }
