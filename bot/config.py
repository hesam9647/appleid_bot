import os
from dotenv import load_dotenv

# بارگذاری فایل .env
load_dotenv()

def load_config():
    # توکن ربات تلگرام
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # در صورتی که توکن معتبر نباشد، برنامه را متوقف می‌کند
    if not BOT_TOKEN:
        raise ValueError("توکن ربات معتبر نیست! لطفاً آن را در فایل .env وارد کنید.")
    
    # تنظیمات دیتابیس (اگر استفاده می‌کنید)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")  # پیش‌فرض sqlite

    # درگاه‌های پرداخت
    ZARINPAL_API_KEY = os.getenv("ZARINPAL_API_KEY", "کد_زرین‌پال")
    IDPAY_API_KEY = os.getenv("IDPAY_API_KEY", "کد_آیدی‌پی")

    # اطلاعات مدیریت
    ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "")
    if ADMIN_USER_IDS:
        ADMIN_USER_IDS = [int(user_id) for user_id in ADMIN_USER_IDS.split(",")]
    else:
        ADMIN_USER_IDS = []

    # تنظیمات دیگر
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

    return {
        "token": BOT_TOKEN,
        "database_url": DATABASE_URL,
        "zarinpal_api_key": ZARINPAL_API_KEY,
        "idpay_api_key": IDPAY_API_KEY,
        "admin_user_ids": ADMIN_USER_IDS,
        "logging_level": LOGGING_LEVEL
    }
