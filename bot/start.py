import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# بارگذاری تنظیمات از فایل config
from bot.config import load_config

async def main():
    config = load_config()

    # توکن ربات تلگرام
    bot = Bot(token=config["token"], default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # ادامه تنظیمات و راه‌اندازی ربات
    print("✅ ربات با موفقیت اجرا شد.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
