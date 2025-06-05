# apple_id_bot/handlers/admin_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db_handler import DatabaseManager
from config.config import ADMIN_IDS
import json

db = DatabaseManager()

# States for conversation
WAITING_FOR_EMAIL, WAITING_FOR_PASSWORD, WAITING_FOR_EMAIL_PASS, \
WAITING_FOR_BIRTH, WAITING_FOR_SECURITY_Q1, WAITING_FOR_SECURITY_A1, \
WAITING_FOR_SECURITY_Q2, WAITING_FOR_SECURITY_A2, \
WAITING_FOR_SECURITY_Q3, WAITING_FOR_SECURITY_A3, \
WAITING_FOR_BROADCAST, WAITING_FOR_USER_NOTE = range(12)

def is_admin(user_id: int) -> bool:
    """چک کردن ادمین بودن کاربر"""
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل اصلی ادمین"""
    if not is_admin(update.effective_user.id):
        return
    
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
    
    text = "🔰 پنل مدیریت\n\nخوش آمدید. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران"""
    query = update.callback_query
    await query.answer()
    
    users = db.get_all_users()
    keyboard = []
    
    # فیلترهای کاربران
    keyboard.append([
        InlineKeyboardButton("👥 همه", callback_data='filter_all'),
        InlineKeyboardButton("🚫 بلاک شده", callback_data='filter_blocked'),
        InlineKeyboardButton("💰 خریداران", callback_data='filter_buyers')
    ])
    
    # لیست کاربران
    for user in users[:5]:  # نمایش 5 کاربر اول
        status = "🚫" if user['is_blocked'] else "✅"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {user['username']} - موجودی: {user['balance']:,}",
                callback_data=f"user_{user['user_id']}"
            )
        ])
    
    # دکمه‌های ناوبری
    keyboard.append([
        InlineKeyboardButton("⬅️ قبلی", callback_data='prev_users'),
        InlineKeyboardButton("➡️ بعدی", callback_data='next_users')
    ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')])
    
    await query.message.edit_text(
        "👥 مدیریت کاربران\n\n"
        "• برای مدیریت هر کاربر، روی نام آن کلیک کنید\n"
        "• از فیلترها برای مرتب‌سازی استفاده کنید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربر خاص"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[1])
    user = db.get_user(user_id)
    
    if not user:
        await query.message.edit_text(
            "❌ کاربر یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='admin_users')
            ]])
        )
        return
    
    status = "🚫 بلاک شده" if user['is_blocked'] else "✅ فعال"
    keyboard = [
        [
            InlineKeyboardButton(
                "🚫 بلاک" if not user['is_blocked'] else "✅ آنبلاک",
                callback_data=f"toggle_block_{user_id}"
            ),
            InlineKeyboardButton("💰 افزایش موجودی", callback_data=f"add_balance_{user_id}")
        ],
        [
            InlineKeyboardButton("📝 یادداشت", callback_data=f"add_note_{user_id}"),
            InlineKeyboardButton("📨 ارسال پیام", callback_data=f"send_message_{user_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='admin_users')]
    ]
    
    text = (
        f"👤 مدیریت کاربر\n\n"
        f"🆔 شناسه: {user_id}\n"
        f"👤 نام کاربری: {user['username']}\n"
        f"💰 موجودی: {user['balance']:,} تومان\n"
        f"⭐️ وضعیت: {status}\n"
        f"📅 تاریخ عضویت: {user['created_at']}\n"
    )
    
    if user.get('note'):
        text += f"\n📝 یادداشت:\n{user['note']}"
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def add_apple_id_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند افزودن اپل آیدی"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['apple_id'] = {}
    
    await query.message.edit_text(
        "🍎 افزودن اپل آیدی جدید\n\n"
        "لطفاً ایمیل اپل آیدی را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 انصراف", callback_data='admin_apple_ids')
        ]])
    )
    
    return WAITING_FOR_EMAIL

async def add_apple_id_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت ایمیل اپل آیدی"""
    context.user_data['apple_id']['email'] = update.message.text
    
    await update.message.reply_text(
        "✅ ایمیل ذخیره شد\n\n"
        "حالا لطفاً رمز اپل آیدی را وارد کنید:"
    )
    
    return WAITING_FOR_PASSWORD

# ادامه توابع مربوط به دریافت اطلاعات اپل آیدی...

async def save_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره نهایی اپل آیدی"""
    apple_id_data = context.user_data['apple_id']
    
    success = db.add_apple_id(apple_id_data)
    
    if success:
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data='admin_apple_ids')]]
        await update.message.reply_text(
            "✅ اپل آیدی با موفقیت ذخیره شد!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("❌ خطا در ذخیره اپل آیدی!")
    
    return ConversationHandler.END

# اضافه کردن سایر توابع مورد نیاز...
