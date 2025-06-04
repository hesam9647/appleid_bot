# apple_id_bot/handlers/user_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager

db = DatabaseManager()

async def handle_buy_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بخش خرید سرویس"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔰 اپل آیدی معمولی - 100,000 تومان", callback_data='buy_normal')],
        [InlineKeyboardButton("⭐️ اپل آیدی ویژه - 200,000 تومان", callback_data='buy_premium')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
    ]
    
    await query.message.edit_text(
        "🛍 خرید اپل آیدی\n\n"
        "لطفاً نوع سرویس مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بخش کیف پول"""
    query = update.callback_query
    await query.answer()
    
    user = db.get_user(query.from_user.id)
    balance = user['balance'] if user else 0
    
    keyboard = [
        [InlineKeyboardButton("💳 افزایش موجودی", callback_data='add_funds')],
        [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data='transactions')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
    ]
    
    await query.message.edit_text(
        f"💰 کیف پول\n\n"
        f"موجودی فعلی شما: {balance:,} تومان\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بازگشت به منوی اصلی"""
    query = update.callback_query
    await query.answer()
    
    from keyboards.user_keyboards import main_menu_keyboard
    await query.message.edit_text(
        "به ربات فروش اپل آیدی خوش آمدید!",
        reply_markup=main_menu_keyboard()
    )

async def handle_buy_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر تایید خرید"""
    query = update.callback_query
    await query.answer()
    
    apple_id_type = query.data.split('_')[1]  # normal یا premium
    price = 100000 if apple_id_type == 'normal' else 200000
    
    user = db.get_user(query.from_user.id)
    if not user or user['balance'] < price:
        keyboard = [
            [InlineKeyboardButton("💳 افزایش موجودی", callback_data='add_funds')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_buy')]
        ]
        await query.message.edit_text(
            "❌ موجودی کافی نیست!\n"
            f"موجودی مورد نیاز: {price:,} تومان\n"
            f"موجودی فعلی: {user['balance']:,} تومان",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # چک کردن موجود بودن اپل آیدی
    available_apple_id = db.get_available_apple_id(apple_id_type)
    if not available_apple_id:
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_buy')]]
        await query.message.edit_text(
            "❌ متأسفانه در حال حاضر اپل آیدی موجود نیست!\n"
            "لطفاً بعداً مراجعه کنید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ تأیید و خرید", callback_data=f'confirm_buy_{apple_id_type}')],
        [InlineKeyboardButton("❌ انصراف", callback_data='back_to_buy')]
    ]
    
    await query.message.edit_text(
        f"📝 پیش‌نمایش خرید:\n\n"
        f"نوع: {'معمولی' if apple_id_type == 'normal' else 'ویژه'}\n"
        f"قیمت: {price:,} تومان\n"
        f"موجودی شما: {user['balance']:,} تومان\n\n"
        "آیا مایل به خرید هستید؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
