import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from bot.handlers.admin import register_admin_handlers  # اضافه کن

from bot.config import Config
from bot.utils.db import create_db
from bot.handlers import start  # ✅ اضافه شد
# فایل bot/main.py
from bot.handlers.start import register_start_handlers  # اصلاح شده
def register_routers(dp):
    register_start_handlers(dp)
    register_admin_handlers(dp)  # ✅ اضافه کن برای وصل کردن admin handler


def register_routers(dp):
    register_start_handlers(dp)  # ثبت هندلرهای شروع
    
load_dotenv()

async def main():
    config = Config()
    bot = Bot(token=config.token, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    # ثبت همه روت‌ها
    register_routers(dp)

    # ساخت دیتابیس
    await create_db(config.database_url)

    print("🤖 ربات اجرا شد!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
