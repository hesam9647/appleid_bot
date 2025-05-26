import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers.user import router as user_router
from app.database import init_db

async def main():
    # تنظیمات لاگ‌ها
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # بارگذاری تنظیمات
    config = load_config()

    # ایجاد بات با تنظیمات جدید Aiogram 3.7
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # ایجاد Dispatcher
    dp = Dispatcher()

    # مقداردهی اولیه پایگاه‌داده (در صورت نیاز)
    db_session = init_db(config.db.database)

    # افزودن روت‌های کاربری
    dp.include_router(user_router)

    # اجرای ربات
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
