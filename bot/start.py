import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram import F

from bot.config import load_config

# بارگذاری تنظیمات
config = load_config()
BOT_TOKEN = config["token"]

# ساخت بات و دیسپچر
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# هندلر /start
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("مشاهده جزئیات حساب"),
        types.KeyboardButton("خرید اپل آیدی")
    )
    await message.answer("سلام! به ربات فروش اپل آیدی خوش آمدید.", reply_markup=markup)

# تابع main برای راه‌اندازی ربات
async def main():
    await dp.start_polling(bot)

# اجرای برنامه
if __name__ == "__main__":
    asyncio.run(main())
