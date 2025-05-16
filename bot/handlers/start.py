from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.db import get_user_balance, update_balance

async def on_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("مشاهده جزئیات حساب")
    button2 = KeyboardButton("خرید اپل آیدی")
    markup.add(button1, button2)
    
    user_id = message.from_user.id

    # چک کردن موجودی کاربر و در صورت نبود مقدار اولیه صفر بگذار
    user_balance = get_wallet(user_id)
    if user_balance == 0:
        update_wallet(user_id, 0)  # اگر لازم داری کاربر رو اضافه کنی، بهتره اول add_user رو صدا بزنی
    
    await message.answer("سلام! به ربات فروش اپل آیدی خوش آمدید.\nلطفا یک گزینه را انتخاب کنید.", reply_markup=markup)
