# apple_id_bot/handlers/ticket_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from database.db_handler import DatabaseManager
from config.config import ADMIN_IDS
import datetime

db = DatabaseManager()

# States
WAITING_FOR_TITLE, WAITING_FOR_MESSAGE, WAITING_FOR_REPLY = range(3)

async def start_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ایجاد تیکت جدید"""
    query = update.callback_query
    await query.answer()
    
    categories = [
        "❓ سوال عمومی",
        "🛍 مشکل در خرید",
        "💰 مشکل مالی",
        "🎟 مشکل اپل آیدی",
        "🔄 درخواست بازگشت وجه",
        "📦 پیگیری سفارش"
    ]
    
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat, callback_data=f'ticket_cat_{cat}')])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')])
    
    await query.message.edit_text(
        "🎫 ایجاد تیکت جدید\n\n"
        "👈 لطفاً موضوع تیکت را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def get_ticket_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت متن تیکت"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.split('_')[2]
    context.user_data['ticket_category'] = category
    
    await query.message.edit_text(
        f"📝 ایجاد تیکت - {category}\n\n"
        "لطفاً متن پیام خود را به طور کامل ارسال کنید:\n\n"
        "💡 نکات مهم:\n"
        "• تمام جزئیات را ذکر کنید\n"
        "• می‌توانید عکس هم ارسال کنید\n"
        "• برای لغو، دستور /cancel را بزنید",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ انصراف", callback_data='cancel_ticket')
        ]])
    )
    
    return WAITING_FOR_MESSAGE

async def save_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره تیکت"""
    message = update.message.text
    category = context.user_data.get('ticket_category', 'عمومی')
    user_id = update.effective_user.id
    
    # ذخیره تیکت در دیتابیس
    ticket_id = db.create_ticket(user_id, category, message)
    
    # ارسال نوتیفیکیشن به ادمین‌ها
    admin_text = (
        "🎫 تیکت جدید\n\n"
        f"👤 کاربر: {update.effective_user.username}\n"
        f"📋 موضوع: {category}\n"
        f"🔑 شناسه: #{ticket_id}\n\n"
        f"📝 متن پیام:\n{message}"
    )
    
    admin_keyboard = [[
        InlineKeyboardButton("📝 پاسخ", callback_data=f'reply_ticket_{ticket_id}'),
        InlineKeyboardButton("❌ بستن", callback_data=f'close_ticket_{ticket_id}')
    ]]
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
        except Exception as e:
            print(f"Error notifying admin {admin_id}: {e}")
    
    # پاسخ به کاربر
    keyboard = [
        [InlineKeyboardButton("📋 مشاهده تیکت‌های من", callback_data='my_tickets')],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data='back_to_main')]
    ]
    
    await update.message.reply_text(
        "✅ تیکت شما با موفقیت ثبت شد\n\n"
        f"🔑 شماره پیگیری: #{ticket_id}\n"
        "پاسخ تیکت به زودی ارسال خواهد شد.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

async def view_my_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهده تیکت‌های کاربر"""
    query = update.callback_query
    await query.answer()
    
    tickets = db.get_user_tickets(query.from_user.id)
    
    if not tickets:
        await query.message.edit_text(
            "📋 تیکت‌های من\n\n"
            "شما هیچ تیکتی ندارید!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 تیکت جدید", callback_data='new_ticket')],
                [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
            ])
        )
        return
    
    tickets_text = "📋 تیکت‌های من\n\n"
    keyboard = []
    
    for ticket in tickets:
        status_emoji = {
            'open': '🟢',
            'answered': '📝',
            'closed': '🔴'
        }.get(ticket['status'], '⚪️')
        
        tickets_text += (
            f"{status_emoji} تیکت #{ticket['id']}\n"
            f"📋 موضوع: {ticket['category']}\n"
            f"📅 تاریخ: {ticket['created_at']}\n"
            f"📊 وضعیت: {ticket['status']}\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
        )
        
        keyboard.append([
            InlineKeyboardButton(
                f"مشاهده تیکت #{ticket['id']}",
                callback_data=f'view_ticket_{ticket["id"]}'
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("📝 تیکت جدید", callback_data='new_ticket')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
    ])
    
    await query.message.edit_text(
        tickets_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهده جزئیات یک تیکت"""
    query = update.callback_query
    await query.answer()
    
    ticket_id = int(query.data.split('_')[2])
    ticket = db.get_ticket_details(ticket_id)
    
    if not ticket:
        await query.message.edit_text(
            "❌ تیکت یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='my_tickets')
            ]])
        )
        return
    
    status_emoji = {
        'open': '🟢',
        'answered': '📝',
        'closed': '🔴'
    }.get(ticket['status'], '⚪️')
    
    ticket_text = (
        f"{status_emoji} تیکت #{ticket['id']}\n\n"
        f"📋 موضوع: {ticket['category']}\n"
        f"📅 تاریخ: {ticket['created_at']}\n"
        f"📊 وضعیت: {ticket['status']}\n\n"
        "📝 متن پیام:\n"
        f"{ticket['message']}\n\n"
    )
    
    # اضافه کردن پاسخ‌ها
    if ticket['replies']:
        ticket_text += "\n💬 پاسخ‌ها:\n"
        for reply in ticket['replies']:
            sender = "👤 شما:" if reply['is_user'] else "👨‍💼 پشتیبانی:"
            ticket_text += f"\n{sender}\n{reply['message']}\n"
    
    keyboard = []
    if ticket['status'] != 'closed':
        keyboard.append([InlineKeyboardButton("📝 ارسال پاسخ", callback_data=f'reply_to_{ticket_id}')])
    
    keyboard.extend([
        [InlineKeyboardButton("🔙 بازگشت به لیست", callback_data='my_tickets')],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data='back_to_main')]
    ])
    
    await query.message.edit_text(
        ticket_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
