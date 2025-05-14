# ✅ bot/keyboards/inline.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def product_buttons(products):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for product in products:
        # هر دکمه مربوط به یک محصول خاص
        button = InlineKeyboardButton(text=product["name"], callback_data=f"buy_{product['id']}")
        keyboard.add(button)
    return keyboard
