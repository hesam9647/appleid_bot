import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()


class Config:
    def __init__(self):
        # توکن بات
        self.token = os.getenv("BOT_TOKEN")

        # آدرس دیتابیس (مقدار پیش‌فرض SQLite)
        self.database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3")

        # لیست ادمین‌ها (آیدی‌های عددی، جدا شده با کاما)
        self.admins = [int(i) for i in os.getenv("ADMINS", "").split(",") if i.strip().isdigit()]


def load_config():
    return Config()
