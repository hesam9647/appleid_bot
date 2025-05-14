from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("🛒 خرید اپل آیدی")]], resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("📊 آمار")],
            [KeyboardButton("➕ افزودن محصول")]
        ], resize_keyboard=True
    )

