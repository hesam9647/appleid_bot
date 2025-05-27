import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
import sentry_sdk

from app.config import load_config
from app.database import init_db
from app.middlewares import (
    DatabaseMiddleware,
    CacheMiddleware,      # ← این رو اضافه کن بجای ThrottlingMiddleware
    AuthMiddleware,
    LoggingMiddleware
)

from app.handlers import (
    admin_router,
    user_router,
    error_router,
    payment_router,
    product_router
)
from app.services.backup_service import BackupService
from app.utils.logger import setup_logger

# Setup Sentry for error tracking
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)

async def main():
    # Load config
    config = load_config()
    
    # Setup logging
    logger = setup_logger()
    
    # Initialize Redis
    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password
    )
    
    # Initialize storage for FSM
    storage = RedisStorage(redis=redis)
    
    # Initialize bot and dispatcher
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    
    # Initialize database
    session_pool = await init_db(config.db.database_url)
    
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    
    # Register middlewares
    dp.message.middleware(DatabaseMiddleware(session_pool))
    dp.callback_query.middleware(DatabaseMiddleware(session_pool))
    
    dp.message.middleware(CacheMiddleware(redis))
    dp.callback_query.middleware(CacheMiddleware(redis))
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    dp.message.middleware(LoggingMiddleware(logger))
    dp.callback_query.middleware(LoggingMiddleware(logger))
    
    # Register routers
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(error_router)
    dp.include_router(payment_router)
    dp.include_router(product_router)
    
    # Setup backup service
    backup_service = BackupService(config.backup.path)
    
    # Schedule backup
    scheduler.add_job(
        backup_service.create_backup,
        'cron',
        hour=3,  # Run at 3 AM
        args=[config.db.database_url]
    )
    
    # Schedule cache cleanup
    scheduler.add_job(
        redis.flushdb,
        'cron',
        hour=4  # Run at 4 AM
    )
    
    # Start scheduler
    scheduler.start()
    
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        await redis.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
