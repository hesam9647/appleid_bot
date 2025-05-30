import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers import admin_router, user_router
from app.middlewares import DatabaseMiddleware, ThrottlingMiddleware, AuthMiddleware, LoggingMiddleware  # اگه جدا ساختی

async def main():
    logging.basicConfig(level=logging.INFO)
    
    config = load_config()
    
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()
    
    # ⛳️ اینجا config رو در dispatcher ذخیره می‌کنی نه bot
    dp['config'] = config

    await bot.set_my_commands([
        BotCommand(command="start", description="شروع ربات"),
        BotCommand(command="admin", description="پنل مدیریت")
    ])
    
    # Register middlewares
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
