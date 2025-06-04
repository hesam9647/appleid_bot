# apple_id_bot/main.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

from config.config import BOT_TOKEN
from database.db_handler import DatabaseManager
from keyboards.user_keyboards import main_menu_keyboard

# هندلرهای کاربر
from handlers.user_handler import handle_buy_service, handle_wallet

# هندلرهای پرداخت
from handlers.payment_handler import handle_add_funds, process_payment, verify_payment, handle_back_to_wallet

# هندلرهای ادمین
from handlers.admin_handler import admin_panel, manage_users, manage_apple_ids, add_apple_id

# هندلرهای تیکت
from handlers.ticket_handler import (
    start_ticket, get_ticket_message, save_ticket, view_tickets,
    WAITING_FOR_TITLE, WAITING_FOR_MESSAGE
)

# ایجاد اتصال به دیتابیس
db = DatabaseManager()

# هندلر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اجرای دستورات اولیه هنگام شروع ربات توسط کاربر"""
    user_id = update.effective_user.id
    username = update.effective_user.username

    db.add_user(user_id, username)

    await update.message.reply_text(
        "به ربات فروش اپل آیدی خوش آمدید!",
        reply_markup=main_menu_keyboard()
    )

# هندلر لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات و بازگشت به منوی اصلی"""
    await update.message.reply_text(
        "عملیات لغو شد.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

def main():
    """تابع اصلی برای اجرای ربات"""
    application = Application.builder().token(BOT_TOKEN).build()

    # ✅ هندلرهای اصلی
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))

    # ✅ هندلرهای کاربر
    application.add_handler(CallbackQueryHandler(handle_buy_service, pattern=r'^buy_service$'))
    application.add_handler(CallbackQueryHandler(handle_wallet, pattern=r'^wallet$'))

    # ✅ هندلرهای پرداخت
    application.add_handler(CallbackQueryHandler(handle_add_funds, pattern=r'^add_funds$'))
    application.add_handler(CallbackQueryHandler(process_payment, pattern=r'^pay_\d+$'))
    application.add_handler(CallbackQueryHandler(verify_payment, pattern=r'^verify_payment_\w+$'))
    application.add_handler(CallbackQueryHandler(handle_back_to_wallet, pattern=r'^back_to_wallet$'))

    # ✅ هندلرهای ادمین
    application.add_handler(CallbackQueryHandler(manage_users, pattern=r'^admin_users$'))
    application.add_handler(CallbackQueryHandler(manage_apple_ids, pattern=r'^admin_apple_ids$'))
    application.add_handler(CallbackQueryHandler(add_apple_id, pattern=r'^add_apple_id$'))

    # ✅ هندلرهای تیکت پشتیبانی (ConversationHandler)
    ticket_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_ticket, pattern=r'^new_ticket$')],
        states={
            WAITING_FOR_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ticket_message)],
            WAITING_FOR_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_ticket)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(ticket_conv_handler)
    application.add_handler(CallbackQueryHandler(view_tickets, pattern=r'^view_tickets$'))

    # ✅ اجرای ربات
    print("✅ Bot started successfully...")
    application.run_polling()

if __name__ == '__main__':
    main()
