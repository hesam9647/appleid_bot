from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from database.db_handler import DatabaseManager
from utils.decorators import admin_only

db = DatabaseManager()

# States for conversation handler
WAITING_FOR_BROADCAST, WAITING_FOR_APPLE_ID = range(2)

@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 مدیریت کاربران", callback_data='admin_users'),
         InlineKeyboardButton("🎟 مدیریت اپل آیدی‌ها", callback_data='admin_apple_ids')],
        [InlineKeyboardButton("💰 گزارش مالی", callback_data='admin_financial'),
         InlineKeyboardButton("📨 ارسال پیام همگانی", callback_data='admin_broadcast')],
        [InlineKeyboardButton("🎫 مدیریت تیکت‌ها", callback_data='admin_tickets'),
         InlineKeyboardButton("📊 آمار", callback_data='admin_stats')]
    ]
    
    await update.message.reply_text(
        "🔰 پنل مدیریت\n"
        "خوش آمدید. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@admin_only
async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    users = db.get_all_users()
    
    user_list_text = "👥 لیست کاربران:\n\n"
    for user in users:
        user_list_text += f"• {user['user_id']} - {user.get('username', 'ندارد')}\n"
        
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')]]
    
    await query.message.edit_text(user_list_text, reply_markup=InlineKeyboardMarkup(keyboard))

@admin_only
async def manage_apple_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    apple_ids = db.get_all_apple_ids()
    
    apple_ids_text = "🎟 لیست اپل آیدی‌ها:\n\n"
    for apple_id in apple_ids:
        apple_ids_text += f"• {apple_id['apple_id']} - وضعیت: {apple_id.get('status', 'نامشخص')}\n"
        
    keyboard = [
        [InlineKeyboardButton("➕ اضافه کردن اپل آیدی جدید", callback_data='add_apple_id')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')]
    ]
    
    await query.message.edit_text(apple_ids_text, reply_markup=InlineKeyboardMarkup(keyboard))

@admin_only
async def add_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.message.edit_text(
        "🎟 لطفاً اپل آیدی جدید را ارسال کنید:\n"
        "- برای لغو، دستور /cancel را ارسال کنید."
    )
    
    return WAITING_FOR_APPLE_ID

# به صورت نمونه اینجا تابعی برای دریافت اپل آیدی جدید هم میتونی اضافه کنی که تو حالت WAITING_FOR_APPLE_ID کار کنه
@admin_only
async def receive_new_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_apple_id = update.message.text
    db.add_apple_id(new_apple_id)  # فرض بر این است که این تابع در DatabaseManager پیاده شده است
    
    await update.message.reply_text(
        f"✅ اپل آیدی {new_apple_id} با موفقیت اضافه شد."
    )
    return ConversationHandler.END
