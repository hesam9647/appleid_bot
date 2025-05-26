import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import load_config
from app.handlers.user import router as user_router
from app.database import init_db

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    config = load_config()
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher()

    # Initialize database
    db_session = init_db(config.db.database)

    # Register routers
    dp.include_router(user_router)

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
