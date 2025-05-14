from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.config import ADMIN_ID

async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton("مشاهده تراکنش‌ها")
        button2 = KeyboardButton("مدیریت کاربران")
        markup.add(button1, button2)
        await message.answer("به پنل مدیریت خوش آمدید!", reply_markup=markup)
