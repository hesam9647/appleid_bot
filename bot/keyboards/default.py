from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="مشاهده محصولات", callback_data="view_products"),
        InlineKeyboardButton(text="تماس با پشتیبانی", callback_data="support")
    )
    return keyboard
