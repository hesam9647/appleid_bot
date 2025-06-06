from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# کانفیگ
from config.config import BOT_TOKEN

# دیتابیس
from database.db_handler import DatabaseManager

# کیبورد
from keyboards.user_keyboards import main_menu_keyboard

# هندلرهای راهنما
from handlers.help_handler import (
    show_help, show_purchase_help, show_payment_help,
    show_faq, show_rules
)

# هندلرهای کاربر
from handlers.user_handler import (
    handle_buy_service, handle_wallet, handle_buy_confirmation,
    handle_purchase_history
)

# هندلرهای پرداخت
from handlers.payment_handler import (
    handle_add_funds, process_payment, verify_payment, handle_back_to_wallet
)

# هندلرهای اپل آیدی و ادمین
from handlers.admin_handler import (
    admin_panel, manage_users as handle_admin_users,
    manage_user as handle_user_management,
    manage_apple_ids as handle_admin_apple_ids,
    list_apple_ids, manage_single_apple_id,
    add_apple_id_start, add_apple_id_email, add_apple_id_password,
    add_apple_id_email_pass, add_apple_id_birth,
    add_apple_id_security_q1, add_apple_id_security_a1,
    add_apple_id_security_q2, add_apple_id_security_a2,
    add_apple_id_security_q3, add_apple_id_security_a3,
    confirm_apple_id, handle_admin_financial,
    handle_admin_broadcast, handle_admin_tickets,
    handle_admin_settings, handle_apple_id_management,
    handle_back, handle_edit_texts, handle_edit_prices,
    handle_manage_admins, handle_security_settings, handle_channel_settings,
    start_edit_text, save_edited_text, start_edit_price, save_edited_price,
    WAITING_FOR_TEXT, WAITING_FOR_PRICE
)

# هندلرهای تیکت
from handlers.ticket_handler import (
    start_ticket, get_ticket_message, save_ticket, view_tickets,
    WAITING_FOR_TITLE, WAITING_FOR_MESSAGE
)

# ✅ دیتابیس
db = DatabaseManager()

# ✅ هندلر /start
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    db.add_user(user_id, username)

    await update.message.reply_text(
        "به ربات فروش اپل آیدی خوش آمدید!",
        reply_markup=main_menu_keyboard()
    )

# ✅ لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ✅ تابع اصلی
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # ---------------- هندلرهای راهنما ----------------
    application.add_handler(CallbackQueryHandler(show_help, pattern=r'^help$'))
    application.add_handler(CallbackQueryHandler(show_purchase_help, pattern=r'^help_purchase$'))
    application.add_handler(CallbackQueryHandler(show_payment_help, pattern=r'^help_payment$'))
    application.add_handler(CallbackQueryHandler(show_faq, pattern=r'^help_faq$'))
    application.add_handler(CallbackQueryHandler(show_rules, pattern=r'^help_rules$'))

    # ---------------- هندلرهای اپل آیدی ----------------
    apple_id_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_apple_id_start, pattern=r'^add_apple_id$')],
        states={
            WAITING_FOR_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_email)],
            WAITING_FOR_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_password)],
            WAITING_FOR_EMAIL_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_email_pass)],
            WAITING_FOR_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_birth)],
            WAITING_FOR_SECURITY_Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_security_q1)],
            WAITING_FOR_SECURITY_A1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_security_a1)],
            WAITING_FOR_SECURITY_Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_security_q2)],
            WAITING_FOR_SECURITY_A2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_security_a2)],
            WAITING_FOR_SECURITY_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_security_q3)],
            WAITING_FOR_SECURITY_A3: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apple_id_security_a3)],
        },
        fallbacks=[
            CallbackQueryHandler(confirm_apple_id, pattern=r'^confirm_apple_id$'),
            CallbackQueryHandler(admin_panel, pattern=r'^cancel_apple_id$'),
        ],
        per_message=True
    )
    application.add_handler(apple_id_conv_handler)
    application.add_handler(CallbackQueryHandler(list_apple_ids, pattern=r'^list_apple_ids$'))
    application.add_handler(CallbackQueryHandler(manage_single_apple_id, pattern=r'^apple_id_\d+$'))

    # ---------------- هندلرهای تیکت ----------------
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

    # ---------------- هندلرهای تنظیمات (متن، قیمت و امنیت) ----------------
    settings_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_edit_text, pattern=r'^edit_text_'),
            CallbackQueryHandler(start_edit_price, pattern=r'^change_price_')
        ],
        states={
            WAITING_FOR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_text)],
            WAITING_FOR_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_price)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(handle_admin_settings, pattern=r'^back_to_settings$')
        ]
    )
    application.add_handler(settings_handler)
    application.add_handler(CallbackQueryHandler(handle_edit_texts, pattern=r'^edit_texts$'))
    application.add_handler(CallbackQueryHandler(handle_edit_prices, pattern=r'^edit_prices$'))
    application.add_handler(CallbackQueryHandler(handle_manage_admins, pattern=r'^manage_admins$'))
    application.add_handler(CallbackQueryHandler(handle_security_settings, pattern=r'^security_settings$'))
    application.add_handler(CallbackQueryHandler(handle_channel_settings, pattern=r'^channel_settings$'))

    # ---------------- هندلرهای کاربر ----------------
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(handle_buy_service, pattern=r'^buy_service$'))
    application.add_handler(CallbackQueryHandler(handle_buy_confirmation, pattern=r'^buy_'))
    application.add_handler(CallbackQueryHandler(handle_wallet, pattern=r'^wallet$'))
    application.add_handler(CallbackQueryHandler(handle_purchase_history, pattern=r'^purchase_history$'))

    # ---------------- هندلرهای پرداخت ----------------
    application.add_handler(CallbackQueryHandler(handle_add_funds, pattern=r'^add_funds$'))
    application.add_handler(CallbackQueryHandler(process_payment, pattern=r'^pay_\d+$'))
    application.add_handler(CallbackQueryHandler(verify_payment, pattern=r'^verify_payment_\w+$'))
    application.add_handler(CallbackQueryHandler(handle_back_to_wallet, pattern=r'^back_to_wallet$'))

    # ---------------- هندلرهای ادمین ----------------
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(handle_admin_users, pattern=r'^admin_users$'))
    application.add_handler(CallbackQueryHandler(handle_admin_apple_ids, pattern=r'^admin_apple_ids$'))
    application.add_handler(CallbackQueryHandler(handle_admin_financial, pattern=r'^admin_financial$'))
    application.add_handler(CallbackQueryHandler(handle_admin_broadcast, pattern=r'^admin_broadcast$'))
    application.add_handler(CallbackQueryHandler(handle_admin_tickets, pattern=r'^admin_tickets$'))
    application.add_handler(CallbackQueryHandler(handle_admin_settings, pattern=r'^admin_settings$'))
    application.add_handler(CallbackQueryHandler(handle_user_management, pattern=r'^manage_user_\d+$'))
    application.add_handler(CallbackQueryHandler(handle_apple_id_management, pattern=r'^manage_apple_id_\d+$'))
    application.add_handler(CallbackQueryHandler(handle_back, pattern=r'^back_to_'))

    # ---------------- اجرای ربات ----------------
    print("✅ Bot started successfully...")
    application.run_polling()

# ✅ اجرای تابع اصلی
if __name__ == '__main__':
    main()
