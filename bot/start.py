import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from bot.config import load_config
from bot.utils.db import create_db
from bot.main import register_routers

# بارگذاری متغیرهای محیطی
load_dotenv()
config = load_config()

async def main():
    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    register_routers(dp)
    await create_db(config.database_url)

    print("✅ ربات با موفقیت اجرا شد.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
