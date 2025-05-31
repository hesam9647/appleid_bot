import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import load_config
from app.handlers import admin_router, user_router
from app.middlewares import (
    DatabaseMiddleware,
    ThrottlingMiddleware,
    AuthMiddleware,
    LoggingMiddleware
)
from app.utils.logger import setup_logger

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="شروع ربات"),
        BotCommand(command="admin", description="پنل مدیریت"),
        BotCommand(command="help", description="راهنما"),
        BotCommand(command="profile", description="پروفایل"),
    ]
    await bot.set_my_commands(commands)

async def setup_middlewares(dp: Dispatcher, bot: Bot, config):
    # Setup database middleware
    db_middleware = DatabaseMiddleware()
    dp.message.middleware(db_middleware)
    dp.callback_query.middleware(db_middleware)
    
    # Setup throttling middleware
    throttling_middleware = ThrottlingMiddleware()
    dp.message.middleware(throttling_middleware)
    dp.callback_query.middleware(throttling_middleware)
    
    # Setup auth middleware with config
    auth_middleware = AuthMiddleware(config)
    dp.message.middleware(auth_middleware)
    dp.callback_query.middleware(auth_middleware)
    
    # Setup logging middleware
    logging_middleware = LoggingMiddleware()
    dp.message.middleware(logging_middleware)
    dp.callback_query.middleware(logging_middleware)

async def main():
    # Setup logging
    logger = setup_logger()
    logger.info("Starting bot...")
    
    # Load config
    config = load_config()
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Setup bot commands
    await setup_bot_commands(bot)
    
    # Setup middlewares with config
    await setup_middlewares(dp, bot, config)
    
    # Register routers with config
    admin_router.message.filter(lambda message: message.from_user.id in config.tg_bot.admin_ids)
    admin_router.callback_query.filter(lambda call: call.from_user.id in config.tg_bot.admin_ids)
    
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    try:
        logger.info("Bot started successfully!")
        await dp.start_polling(bot, config=config)
    finally:
        logger.info("Bot stopped!")
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user!")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
