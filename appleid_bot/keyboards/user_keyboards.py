# apple_id_bot/keyboards/user_keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """منوی اصلی کاربر"""
    keyboard = [
        [InlineKeyboardButton("🛍 فروشگاه اپل آیدی", callback_data='buy_service')],
        [
            InlineKeyboardButton("💰 کیف پول", callback_data='wallet'),
            InlineKeyboardButton("📋 سوابق خرید", callback_data='purchase_history')
        ],
        [
            InlineKeyboardButton("🎫 ارسال تیکت", callback_data='new_ticket'),
            InlineKeyboardButton("📨 تیکت‌های من", callback_data='my_tickets')
        ],
        [
            InlineKeyboardButton("📚 راهنما", callback_data='help'),
            InlineKeyboardButton("ℹ️ قوانین", callback_data='rules')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def buy_service_keyboard() -> InlineKeyboardMarkup:
    """منوی خرید سرویس"""
    keyboard = [
        [InlineKeyboardButton("✨ اپل آیدی ویژه | 200,000 تومان", callback_data='buy_premium')],
        [InlineKeyboardButton("🔰 اپل آیدی معمولی | 100,000 تومان", callback_data='buy_normal')],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def wallet_keyboard(balance: int) -> InlineKeyboardMarkup:
    """منوی کیف پول"""
    keyboard = [
        [InlineKeyboardButton(f"💰 موجودی فعلی: {balance:,} تومان", callback_data='none')],
        [InlineKeyboardButton("💳 افزایش موجودی", callback_data='add_funds')],
        [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data='transactions')],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_amount_keyboard() -> InlineKeyboardMarkup:
    """منوی انتخاب مبلغ شارژ"""
    keyboard = [
        [InlineKeyboardButton("💰 50,000 تومان", callback_data='pay_50000')],
        [InlineKeyboardButton("💰 100,000 تومان", callback_data='pay_100000')],
        [InlineKeyboardButton("💰 200,000 تومان", callback_data='pay_200000')],
        [InlineKeyboardButton("💰 500,000 تومان", callback_data='pay_500000')],
        [InlineKeyboardButton("🔙 بازگشت به کیف پول", callback_data='back_to_wallet')]
    ]
    return InlineKeyboardMarkup(keyboard)

def ticket_keyboard() -> InlineKeyboardMarkup:
    """منوی تیکت"""
    keyboard = [
        [InlineKeyboardButton("📝 تیکت جدید", callback_data='create_ticket')],
        [InlineKeyboardButton("📋 تیکت‌های باز", callback_data='open_tickets')],
        [InlineKeyboardButton("📂 تیکت‌های بسته", callback_data='closed_tickets')],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def help_keyboard() -> InlineKeyboardMarkup:
    """منوی راهنما"""
    keyboard = [
        [
            InlineKeyboardButton("📖 راهنمای خرید", callback_data='help_purchase'),
            InlineKeyboardButton("💳 راهنمای پرداخت", callback_data='help_payment')
        ],
        [
            InlineKeyboardButton("❓ سوالات متداول", callback_data='help_faq'),
            InlineKeyboardButton("📜 قوانین", callback_data='help_rules')
        ],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)
