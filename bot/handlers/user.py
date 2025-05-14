from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.db import get_user_balance

async def show_main_menu(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("مشاهده جزئیات حساب")
    button2 = KeyboardButton("خرید اپل آیدی")
    markup.add(button1, button2)
    await message.answer("لطفا یک گزینه را انتخاب کنید.", reply_markup=markup)

async def view_account_details(message: types.Message):
    user_balance = get_user_balance(message.from_user.id)
    response = f"موجودی شما: {user_balance} تومان"
    await message.answer(response)
