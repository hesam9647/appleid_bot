import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import start  # فرض بر این است که start_router در این ماژول هست
from bot.utils import db
from bot.config import load_config

config = load_config()
BOT_TOKEN = config["token"]  # مطمئن شو که توکن درست بارگذاری شده

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()  # Dispatcher بدون آرگومان

dp.include_router(start.start_router)  # اضافه کردن روت‌ها

async def main():
    db.init_db()  # ساخت جداول دیتابیس در صورت نیاز
    print("🤖 ربات اجرا شد!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
