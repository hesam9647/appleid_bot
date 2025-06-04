# apple_id_bot/keyboards/user_keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """کیبورد منوی اصلی"""
    keyboard = [
        [InlineKeyboardButton("🛍 خرید سرویس", callback_data='buy_service')],
        [InlineKeyboardButton("💬 تیکت و پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("📚 راهنما", callback_data='help')],
        [InlineKeyboardButton("🧾 سوابق خرید", callback_data='history')],
        [InlineKeyboardButton("💰 کیف پول", callback_data='wallet')]
    ]
    return InlineKeyboardMarkup(keyboard)
