import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from bot.utils import db

# بارگذاری فایل .env
load_dotenv()

# گرفتن توکن از .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

# تعریف ربات و دیسپچر
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# هندلر استارت
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    db.add_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 خرید اپل آیدی")],
            [KeyboardButton(text="👜 کیف پول من"), KeyboardButton(text="🛍 سفارش‌های من")],
            [KeyboardButton(text="🎫 تیکت و پشتیبانی")]
        ],
        resize_keyboard=True
    )
    await message.answer("سلام! به پنل کاربری خوش آمدید.", reply_markup=markup)

# هندلر کیف پول
@dp.message(F.text == "👜 کیف پول من")
async def wallet(message: types.Message):
    balance = db.get_wallet(message.from_user.id)
    await message.answer(f"موجودی کیف پول شما: {balance} تومان")

# تابع اصلی
async def main():
    print("🤖 Bot is running...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
