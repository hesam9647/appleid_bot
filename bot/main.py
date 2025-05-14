import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from bot.config import load_config
from bot.utils.db import create_db
from bot.handlers.start import register_start_handlers
from bot.handlers.admin import register_admin_handlers
from bot.handlers.user import register_user_handlers

load_dotenv()

async def main():
    config = load_config()
    bot = Bot(token=config.token, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    await create_db(config.database_url)

    register_start_handlers(dp)
    register_admin_handlers(dp, config.admins)
    register_user_handlers(dp)

    print("🤖 ربات اجرا شد!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
