from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.db import get_user_balance, update_balance

async def on_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("مشاهده جزئیات حساب")
    button2 = KeyboardButton("خرید اپل آیدی")
    markup.add(button1, button2)
    
    # Initializing the user in the database if not exists
    user_balance = get_user_balance(message.from_user.id)
    if user_balance == 0:
        update_balance(message.from_user.id, 0)
    
    await message.answer("سلام! به ربات فروش اپل آیدی خوش آمدید.\nلطفا یک گزینه را انتخاب کنید.", reply_markup=markup)
