from aiogram import Router, types, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.db import get_user_balance, update_balance, add_user

start_router = Router()

@start_router.message(filters.Command("start"))
async def on_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("مشاهده جزئیات حساب")
    button2 = KeyboardButton("خرید اپل آیدی")
    markup.add(button1, button2)
    
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # اگر کاربر جدید است، اضافه‌اش کن
    add_user(user_id, full_name, username)

    # گرفتن موجودی کاربر
    user_balance = get_user_balance(user_id)
    if user_balance == 0:
        update_balance(user_id, 0)  # مقدار اولیه 0 می‌ذاره

    await message.answer("سلام! به ربات فروش اپل آیدی خوش آمدید.\nلطفا یک گزینه را انتخاب کنید.", reply_markup=markup)
