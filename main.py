import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers import admin_router, user_router
from app.middlewares import DatabaseMiddleware, ThrottlingMiddleware, AuthMiddleware, LoggingMiddleware
from app.database import init_db

async def main():
    logging.basicConfig(level=logging.INFO)

    # Load config
    config = load_config()

    # Create bot
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Create dispatcher
    dp = Dispatcher()

    # Inject config into dispatcher context
    dp['config'] = config

    # Set bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="شروع ربات"),
        BotCommand(command="admin", description="پنل مدیریت")
    ])

    # Initialize DB session pool
    SessionLocal = init_db(config.db.database_url)

    # Register middlewares
    db_middleware = DatabaseMiddleware(session_pool=SessionLocal)
    dp.message.middleware(db_middleware)
    dp.callback_query.middleware(db_middleware)

    throttling = ThrottlingMiddleware()
    dp.message.middleware(throttling)
    dp.callback_query.middleware(throttling)

    auth = AuthMiddleware()
    dp.message.middleware(auth)
    dp.callback_query.middleware(auth)

    logging_mw = LoggingMiddleware()
    dp.message.middleware(logging_mw)
    dp.callback_query.middleware(logging_mw)

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
