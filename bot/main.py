import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import start  # فرض می‌کنم start_router تو این ماژول هست
from bot.utils import db
from bot.config import load_config

config = load_config()
BOT_TOKEN = config["token"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start.start_router)

async def main():
    db.init_db()  # اطمینان از اینکه دیتابیس ساخته و آماده است
    print("🤖 ربات اجرا شد!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
