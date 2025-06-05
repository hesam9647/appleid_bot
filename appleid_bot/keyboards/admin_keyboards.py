# apple_id_bot/keyboards/admin_keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_main_keyboard() -> InlineKeyboardMarkup:
    """کیبورد اصلی پنل ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("👥 مدیریت کاربران", callback_data='admin_users'),
            InlineKeyboardButton("🎟 مدیریت اپل آیدی", callback_data='admin_apple_ids')
        ],
        [
            InlineKeyboardButton("💰 گزارش مالی", callback_data='admin_financial'),
            InlineKeyboardButton("📨 پیام همگانی", callback_data='admin_broadcast')
        ],
        [
            InlineKeyboardButton("🎫 مدیریت تیکت‌ها", callback_data='admin_tickets'),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data='admin_settings')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_users_keyboard() -> InlineKeyboardMarkup:
    """کیبورد مدیریت کاربران"""
    keyboard = [
        [
            InlineKeyboardButton("👥 همه کاربران", callback_data='admin_users_all'),
            InlineKeyboardButton("💰 کاربران خریدار", callback_data='admin_users_buyers')
        ],
        [
            InlineKeyboardButton("🚫 کاربران بلاک شده", callback_data='admin_users_blocked'),
            InlineKeyboardButton("✨ VIP کاربران", callback_data='admin_users_vip')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_apple_ids_keyboard() -> InlineKeyboardMarkup:
    """کیبورد مدیریت اپل آیدی"""
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن اپل آیدی", callback_data='add_apple_id'),
            InlineKeyboardButton("📋 لیست موجود", callback_data='list_apple_ids')
        ],
        [
            InlineKeyboardButton("💰 تغییر قیمت‌ها", callback_data='change_prices'),
            InlineKeyboardButton("📊 آمار فروش", callback_data='sales_stats')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)
