import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from bot.config import load_config
from bot.utils.db import create_db
from bot.main import register_routers

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# بارگذاری تنظیمات
config = load_config()

async def main():
    # ساخت بات با توکن از فایل .env
    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # ثبت روت‌ها
    register_routers(dp)

    # اتصال به دیتابیس
    await create_db(config.database_url)

    print("✅ ربات با موفقیت اجرا شد.")
    # شروع poll کردن
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
