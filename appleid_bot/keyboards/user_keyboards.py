# apple_id_bot/keyboards/user_keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """کیبورد منوی اصلی کاربر"""
    keyboard = [
        [InlineKeyboardButton("🛍 فروشگاه اپل آیدی", callback_data='buy_service')],
        [
            InlineKeyboardButton("💰 کیف پول", callback_data='wallet'),
            InlineKeyboardButton("📋 سوابق خرید", callback_data='history')
        ],
        [
            InlineKeyboardButton("🎫 ارسال تیکت", callback_data='new_ticket'),
            InlineKeyboardButton("📜 تیکت‌های من", callback_data='my_tickets')
        ],
        [
            InlineKeyboardButton("📚 راهنما", callback_data='help'),
            InlineKeyboardButton("ℹ️ قوانین", callback_data='rules')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def buy_service_keyboard() -> InlineKeyboardMarkup:
    """کیبورد بخش خرید"""
    keyboard = [
        [InlineKeyboardButton("✨ اپل آیدی ویژه | 200,000 تومان", callback_data='buy_premium')],
        [InlineKeyboardButton("🔰 اپل آیدی معمولی | 100,000 تومان", callback_data='buy_normal')],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def wallet_keyboard(balance: int) -> InlineKeyboardMarkup:
    """کیبورد کیف پول"""
    keyboard = [
        [InlineKeyboardButton("💳 افزایش موجودی", callback_data='add_funds')],
        [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data='transactions')],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)
