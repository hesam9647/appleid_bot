from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram import F
import asyncio

from bot.config import load_config

config = load_config()
BOT_TOKEN = config['token']

# ساخت ربات با تنظیمات پیش‌فرض
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# هندلر دستور /start برای همه کاربران
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 خرید اپل آیدی")],
            [KeyboardButton(text="ℹ️ راهنما"), KeyboardButton(text="📞 پشتیبانی")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "سلام! 👋\nبه ربات فروش اپل آیدی خوش آمدید.\nلطفاً از منوی زیر یک گزینه را انتخاب کنید:",
        reply_markup=markup
    )

# راه‌اندازی ربات
async def main():
    print("✅ ربات با موفقیت اجرا شد.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
