from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.db import add_user, get_wallet, update_wallet

async def on_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("مشاهده جزئیات حساب")
    button2 = KeyboardButton("خرید اپل آیدی")
    markup.add(button1, button2)
    
    user = message.from_user
    add_user(user.id, user.full_name or "", user.username or "")

    user_balance = get_wallet(user.id)
    if user_balance == 0:
        update_wallet(user.id, 0)
    
    await message.answer("سلام! به ربات فروش اپل آیدی خوش آمدید.\nلطفا یک گزینه را انتخاب کنید.", reply_markup=markup)
