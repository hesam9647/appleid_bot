import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers.user import router as user_router
from app.handlers.admin import router as admin_router
from app.database import init_db


async def main():
    # تنظیمات لاگ
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # بارگذاری تنظیمات
    config = load_config()

    # ساخت شی بات
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # ساخت دیسپچر
    dp = Dispatcher()
    
    # اضافه کردن کانفیگ به دیسپچر برای استفاده در میدل‌ویرها
    dp["config"] = config

    # مقداردهی اولیه دیتابیس
    init_db(config.db.database)  # فرض بر sync بودن

    # اضافه کردن روترها
    dp.include_router(user_router)
    dp.include_router(admin_router)

    # شروع ربات
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
