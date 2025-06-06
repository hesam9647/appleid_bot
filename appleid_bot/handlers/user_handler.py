# apple_id_bot/handlers/user_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager
from keyboards.user_keyboards import *
from config.config import ADMIN_IDS
import datetime

db = DatabaseManager()

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دستور شروع"""
    user = update.effective_user
    
    # افزودن یا به‌روزرسانی کاربر در دیتابیس
    db.add_or_update_user(user.id, user.username)
    
    welcome_text = (
        f"👋 سلام {user.first_name} عزیز!\n\n"
        "🎯 به ربات فروش اپل آیدی خوش آمدید\n\n"
        "💫 امکانات ربات:\n"
        "• خرید آسان و سریع اپل آیدی\n"
        "• پشتیبانی 24/7\n"
        "• گارانتی معتبر\n"
        "• قیمت‌های رقابتی\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

async def handle_buy_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بخش خرید سرویس"""
    query = update.callback_query
    await query.answer()
    
    # دریافت لیست اپل آیدی‌های موجود
    available_ids = db.get_available_apple_ids()
    
    if not available_ids:
        await query.message.edit_text(
            "⚠️ در حال حاضر اپل آیدی موجود نیست!\n"
            "لطفاً ساعاتی دیگر مراجعه کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')
            ]])
        )
        return
    
    service_text = (
        "🛍 فروشگاه اپل آیدی\n\n"
        "✨ اپل آیدی ویژه:\n"
        "• امکان تغییر ایمیل و پسورد\n"
        "• پشتیبانی 24/7\n"
        "• گارانتی 3 ماهه\n"
        f"• موجودی: {len([x for x in available_ids if x['type'] == 'premium'])} عدد\n\n"
        "🔰 اپل آیدی معمولی:\n"
        "• تحویل فوری\n"
        "• پشتیبانی عادی\n"
        "• گارانتی 1 ماهه\n"
        f"• موجودی: {len([x for x in available_ids if x['type'] == 'normal'])} عدد\n\n"
        "💡 برای خرید، نوع اپل آیدی را انتخاب کنید:"
    )
    
    await query.message.edit_text(
        service_text,
        reply_markup=buy_service_keyboard()
    )

async def handle_buy_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر تأیید خرید"""
    query = update.callback_query
    await query.answer()
    
    apple_id_type = query.data.split('_')[1]
    price = 200000 if apple_id_type == 'premium' else 100000
    
    # چک کردن موجودی کاربر
    user = db.get_user(query.from_user.id)
    if not user or user['balance'] < price:
        await query.message.edit_text(
            "❌ موجودی کافی نیست!\n\n"
            f"💰 مبلغ مورد نیاز: {price:,} تومان\n"
            f"💳 موجودی فعلی: {user['balance']:,} تومان\n\n"
            "برای افزایش موجودی کلیک کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 افزایش موجودی", callback_data='add_funds')],
                [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_buy')]
            ])
        )
        return

    # چک کردن موجود بودن اپل آیدی
    apple_id = db.get_available_apple_id(apple_id_type)
    if not apple_id:
        await query.message.edit_text(
            "❌ متأسفانه در حال حاضر اپل آیدی موجود نیست!\n"
            "لطفاً بعداً مراجعه کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_buy')
            ]])
        )
        return

    # نمایش پیش‌نمایش خرید
    preview_text = (
        "🛒 پیش‌نمایش خرید:\n\n"
        f"نوع: {'ویژه' if apple_id_type == 'premium' else 'معمولی'}\n"
        f"💰 قیمت: {price:,} تومان\n"
        f"💳 موجودی شما: {user['balance']:,} تومان\n\n"
        "آیا مایل به خرید هستید؟"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید و خرید", callback_data=f'confirm_buy_{apple_id_type}_{apple_id["id"]}'),
            InlineKeyboardButton("❌ انصراف", callback_data='back_to_buy')
        ]
    ]
    
    await query.message.edit_text(
        preview_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر کیف پول"""
    query = update.callback_query
    await query.answer()
    
    user = db.get_user(query.from_user.id)
    balance = user['balance'] if user else 0
    
    # دریافت تراکنش‌های اخیر
    recent_transactions = db.get_user_transactions(query.from_user.id, limit=5)
    
    wallet_text = (
        "💰 کیف پول\n\n"
        f"موجودی فعلی: {balance:,} تومان\n\n"
        "📊 تراکنش‌های اخیر:\n"
    )
    
    if recent_transactions:
        for tx in recent_transactions:
            symbol = "+" if tx['type'] == 'deposit' else "-"
            wallet_text += f"{symbol} {tx['amount']:,} تومان | {tx['created_at']}\n"
    else:
        wallet_text += "هیچ تراکنشی یافت نشد!\n"
    
    await query.message.edit_text(
        wallet_text,
        reply_markup=wallet_keyboard(balance)
    )

async def handle_purchase_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر سوابق خرید"""
    query = update.callback_query
    await query.answer()
    
    purchases = db.get_user_purchases(query.from_user.id)
    
    if not purchases:
        await query.message.edit_text(
            "📋 سوابق خرید\n\n"
            "شما هنوز خریدی انجام نداده‌اید!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🛍 خرید اپل آیدی", callback_data='buy_service'),
                InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')
            ]])
        )
        return
    
    history_text = "📋 سوابق خرید\n\n"
    
    for purchase in purchases:
        history_text += (
            f"🔑 شناسه: {purchase['id']}\n"
            f"📅 تاریخ: {purchase['created_at']}\n"
            f"💰 مبلغ: {purchase['amount']:,} تومان\n"
            f"📦 نوع: {'ویژه' if purchase['type'] == 'premium' else 'معمولی'}\n"
            f"📊 وضعیت: {purchase['status']}\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
        )
    
    keyboard = [
        [InlineKeyboardButton("🛍 خرید جدید", callback_data='buy_service')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
    ]
    
    await query.message.edit_text(
        history_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
