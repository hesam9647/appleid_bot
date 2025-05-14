from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="آمار فروش", callback_data="stats"),
        InlineKeyboardButton(text="افزودن محصول", callback_data="add_product"),
        InlineKeyboardButton(text="مسدود کردن کاربر", callback_data="block_user"),
        InlineKeyboardButton(text="آزاد کردن کاربر", callback_data="unblock_user")
    )
    return keyboard
