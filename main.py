import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers import admin_router, user_router
from app.middlewares import (
    DatabaseMiddleware,
    ThrottlingMiddleware,
    AuthMiddleware,
    LoggingMiddleware
)
from app.database import init_db

async def main():
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Load config
    config = load_config()

    # Create bot
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # ✅ Inject config into bot directly (not dispatcher)
    bot.config = config

    # Create dispatcher
    dp = Dispatcher()

    # Set bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="شروع ربات"),
        BotCommand(command="admin", description="پنل مدیریت")
    ])

    # Initialize DB session pool
    SessionLocal = init_db(config.db.database_url)

    # Register middlewares
    db_middleware = DatabaseMiddleware(session_pool=SessionLocal)
    throttling = ThrottlingMiddleware()
    auth = AuthMiddleware()
    logging_mw = LoggingMiddleware()

    for middleware in [db_middleware, throttling, auth, logging_mw]:
        dp.message.middleware(middleware)
        dp.callback_query.middleware(middleware)

    # Register routers
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🤖 Bot stopped gracefully.")
