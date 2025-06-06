# apple_id_bot/handlers/admin_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager
from keyboards.admin_keyboards import *
from config.config import ADMIN_IDS
import datetime

db = DatabaseManager()

def is_admin(user_id: int) -> bool:
    """چک کردن ادمین بودن کاربر"""
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل اصلی ادمین"""
    if not is_admin(update.effective_user.id):
        return
    
    # دریافت آمار کلی
    stats = db.get_admin_stats()
    
    admin_text = (
        "👤 پنل مدیریت\n\n"
        "📊 آمار کلی:\n"
        f"• کاربران کل: {stats['total_users']}\n"
        f"• کاربران امروز: {stats['today_users']}\n"
        f"• فروش امروز: {stats['today_sales']:,} تومان\n"
        f"• تیکت‌های باز: {stats['open_tickets']}\n"
        f"• اپل آیدی موجود: {stats['available_apple_ids']}\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            admin_text,
            reply_markup=admin_main_keyboard()
        )
    else:
        await update.message.reply_text(
            admin_text,
            reply_markup=admin_main_keyboard()
        )

async def handle_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران"""
    query = update.callback_query
    await query.answer()
    
    # دریافت آمار کاربران
    user_stats = db.get_user_stats()
    
    users_text = (
        "👥 مدیریت کاربران\n\n"
        "📊 آمار کاربران:\n"
        f"• کل کاربران: {user_stats['total']}\n"
        f"• کاربران فعال: {user_stats['active']}\n"
        f"• کاربران بلاک شده: {user_stats['blocked']}\n"
        f"• کاربران خریدار: {user_stats['buyers']}\n"
        f"• کاربران ویژه: {user_stats['vip']}\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    await query.message.edit_text(
        users_text,
        reply_markup=admin_users_keyboard()
    )

async def handle_admin_apple_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت اپل آیدی‌ها"""
    query = update.callback_query
    await query.answer()
    
    # دریافت آمار اپل آیدی‌ها
    apple_id_stats = db.get_apple_id_stats()
    
    apple_ids_text = (
        "🎟 مدیریت اپل آیدی‌ها\n\n"
        "📊 آمار موجودی:\n"
        f"• کل: {apple_id_stats['total']}\n"
        f"• موجود: {apple_id_stats['available']}\n"
        f"• فروخته شده: {apple_id_stats['sold']}\n"
        f"• ویژه موجود: {apple_id_stats['premium_available']}\n"
        f"• معمولی موجود: {apple_id_stats['normal_available']}\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    await query.message.edit_text(
        apple_ids_text,
        reply_markup=admin_apple_ids_keyboard()
    )

async def handle_admin_financial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """گزارش مالی"""
    query = update.callback_query
    await query.answer()
    
    # دریافت آمار مالی
    financial_stats = db.get_financial_stats()
    
    financial_text = (
        "💰 گزارش مالی\n\n"
        "📊 آمار امروز:\n"
        f"• فروش: {financial_stats['today_sales']:,} تومان\n"
        f"• تعداد فروش: {financial_stats['today_orders']} عدد\n"
        f"• شارژ کیف پول: {financial_stats['today_deposits']:,} تومان\n\n"
        "📈 آمار این ماه:\n"
        f"• فروش: {financial_stats['month_sales']:,} تومان\n"
        f"• تعداد فروش: {financial_stats['month_orders']} عدد\n"
        f"• شارژ کیف پول: {financial_stats['month_deposits']:,} تومان\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    await query.message.edit_text(
        financial_text,
        reply_markup=admin_financial_keyboard()
    )

