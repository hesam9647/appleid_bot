import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()


class Config:
    def __init__(self):
        # توکن بات
        self.token = os.getenv("BOT_TOKEN")

        # آدرس دیتابیس (اختیاری، مقدار پیش‌فرض SQLite)
        self.database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3")


def load_config():
    return Config()
