# apple_id_bot/handlers/ticket_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db_handler import DatabaseManager
from config.config import ADMIN_IDS

db = DatabaseManager()

# States
WAITING_FOR_TITLE, WAITING_FOR_MESSAGE = range(2)

async def start_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند ایجاد تیکت جدید"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]]
    
    await query.message.edit_text(
        "🎫 ایجاد تیکت جدید\n\n"
        "لطفاً موضوع تیکت خود را در یک پیام ارسال کنید:\n"
        "- موضوع باید کوتاه و گویا باشد\n"
        "- برای لغو، دستور /cancel را ارسال کنید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return WAITING_FOR_TITLE

async def get_ticket_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت متن اصلی تیکت"""
    title = update.message.text
    context.user_data['ticket_title'] = title
    
    await update.message.reply_text(
        "✅ موضوع تیکت ثبت شد.\n\n"
        "حالا لطفاً متن پیام خود را به طور کامل ارسال کنید:\n"
        "- می‌توانید عکس هم ارسال کنید\n"
        "- برای لغو، دستور /cancel را ارسال کنید"
    )
    
    return WAITING_FOR_MESSAGE

async def save_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره تیکت در دیتابیس"""
    message = update.message.text
    title = context.user_data['ticket_title']
    user_id = update.effective_user.id
    
    ticket_id = db.create_ticket(user_id, title, message)
    
    # ارسال نوتیفیکیشن به ادمین‌ها
    for admin_id in ADMIN_IDS:
        try:
            keyboard = [[InlineKeyboardButton(
                "📝 پاسخ به تیکت", 
                callback_data=f'reply_ticket_{ticket_id}'
            )]]
            
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🎫 تیکت جدید:\n\n"
                     f"از: {update.effective_user.username}\n"
                     f"موضوع: {title}\n"
                     f"متن: {message}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data='back_to_main')]]
    
    await update.message.reply_text(
        "✅ تیکت شما با موفقیت ثبت شد\n"
        "پاسخ تیکت به زودی ارسال خواهد شد.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

async def view_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهده لیست تیکت‌های کاربر"""
    user_id = update.effective_user.id
    tickets = db.get_user_tickets(user_id)
    
    if not tickets:
        keyboard = [[InlineKeyboardButton("🎫 تیکت جدید", callback_data='new_ticket'),
                    InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]]
        
        await update.callback_query.message.edit_text(
            "شما هیچ تیکتی ندارید!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = []
    for ticket in tickets:
        status_emoji = "🟢" if ticket['status'] == 'open' else "🔴"
        keyboard.append([InlineKeyboardButton(
            f"{status_emoji} {ticket['title']} - {ticket['created_at'][:10]}",
            callback_data=f"view_ticket_{ticket['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🎫 تیکت جدید", callback_data='new_ticket')])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')])
    
    await update.callback_query.message.edit_text(
        "📋 لیست تیکت‌های شما:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
