from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def wallet_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزایش موجودی", callback_data="add_balance")],
    ])
