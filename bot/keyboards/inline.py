from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def apple_id_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("اپل آیدی آماده", callback_data="buy_apple_ready"))
    keyboard.add(InlineKeyboardButton("اپل آیدی شخصی", callback_data="buy_apple_personal"))
    return keyboard
