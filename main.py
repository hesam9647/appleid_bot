import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers import admin_router, user_router

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Load config
    config = load_config()
    
    # Initialize bot with default parse_mode
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
