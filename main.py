import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import load_config
from app.database import init_db
from app.handlers import admin_router, user_router
from app.middlewares import DatabaseMiddleware
from app.utils.logger import setup_logger

async def main():
    # Setup logging
    logger = setup_logger()
    logger.info("Starting bot...")
    
    # Load config
    config = load_config()
    
    # Initialize bot and dispatcher
    bot = None
    try:
        # Initialize database
        session_pool = await init_db(config.db.database_url)
        
        # Initialize bot
        bot = Bot(
            token=config.tg_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()

        # Store config and session_pool in dispatcher data
        dp["config"] = config
        dp["session_pool"] = session_pool
        
        # Setup middlewares
        dp.message.middleware(DatabaseMiddleware(session_pool))
        dp.callback_query.middleware(DatabaseMiddleware(session_pool))
        
        # Register admin filter for admin router
        admin_router.message.filter(lambda m: m.from_user.id in config.tg_bot.admin_ids)
        admin_router.callback_query.filter(lambda c: c.from_user.id in config.tg_bot.admin_ids)
        
        # Register routers
        dp.include_router(admin_router)
        dp.include_router(user_router)
        
        # Start polling
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise
    finally:
        if bot is not None:
            logger.info("Closing bot session...")
            await bot.session.close()
        logger.info("Bot stopped!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user!")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
