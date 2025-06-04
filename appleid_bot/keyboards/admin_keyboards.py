# apple_id_bot/handlers/admin_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager
from config.config import ADMIN_IDS
from functools import wraps

db = DatabaseManager()

def admin_only(func):
    """دکوریتور برای چک کردن دسترسی ادمین"""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔️ شما دسترسی به این بخش را ندارید.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل اصلی ادمین"""
    keyboard = [
        [InlineKeyboardButton("👥 مدیریت کاربران", callback_data='admin_users')],
        [InlineKeyboardButton("🎟 مدیریت اپل آیدی‌ها", callback_data='admin_apple_ids')],
        [InlineKeyboardButton("💰 گزارش مالی", callback_data='admin_financial')],
        [InlineKeyboardButton("📨 ارسال پیام همگانی", callback_data='admin_broadcast')]
    ]
    
    await update.message.reply_text(
        "🔰 پنل مدیریت\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@admin_only
async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران"""
    query = update.callback_query
    await query.answer()
    
    # دریافت لیست کاربران از دیتابیس
    users = db.get_all_users()
    
    keyboard = [
        [InlineKeyboardButton(f"👤 {user['username']} - موجودی: {user['balance']:,}", 
                            callback_data=f"user_{user['user_id']}")] 
        for user in users[:10]  # نمایش 10 کاربر اول
    ]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')])
    
    await query.message.edit_text(
        "👥 مدیریت کاربران\n"
        "روی نام کاربر کلیک کنید تا وارد پنل مدیریت آن کاربر شوید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@admin_only
async def manage_apple_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت اپل آیدی‌ها"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("➕ افزودن اپل آیدی جدید", callback_data='add_apple_id')],
        [InlineKeyboardButton("📋 لیست اپل آیدی‌ها", callback_data='list_apple_ids')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')]
    ]
    
    await query.message.edit_text(
        "🎟 مدیریت اپل آیدی‌ها\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@admin_only
async def add_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """افزودن اپل آیدی جدید"""
    query = update.callback_query
    await query.answer()
    
    # ذخیره وضعیت در context برای دریافت اطلاعات در مراحل بعدی
    context.user_data['adding_apple_id'] = True
    
    await query.message.edit_text(
        "🔰 افزودن اپل آیدی جدید\n\n"
        "لطفاً اطلاعات را در قالب زیر ارسال کنید:\n\n"
        "ایمیل: example@icloud.com\n"
        "رمز عبور: password123\n"
        "رمز ایمیل: emailpass123\n"
        "تاریخ تولد: 1990/01/01\n"
        "سوال امنیتی 1: پاسخ 1\n"
        "سوال امنیتی 2: پاسخ 2\n"
        "سوال امنیتی 3: پاسخ 3"
    )
