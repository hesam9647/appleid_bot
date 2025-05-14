from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def admin_keyboard():
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("مدیریت تراکنش‌ها", callback_data="manage_transactions")
    button2 = InlineKeyboardButton("مدیریت کاربران", callback_data="manage_users")
    markup.add(button1, button2)
    return markup
