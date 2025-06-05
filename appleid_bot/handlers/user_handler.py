# apple_id_bot/handlers/user_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager

db = DatabaseManager()

async def handle_buy_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بخش خرید سرویس"""
    query = update.callback_query
    await query.answer()
    
    from keyboards.user_keyboards import buy_service_keyboard
    await query.message.edit_text(
        "🛍 فروشگاه اپل آیدی\n\n"
        "✨ اپل آیدی ویژه:\n"
        "• امکان تغییر ایمیل و پسورد\n"
        "• پشتیبانی ویژه\n"
        "• گارانتی 3 ماهه\n\n"
        "🔰 اپل آیدی معمولی:\n"
        "• تحویل فوری\n"
        "• پشتیبانی عادی\n"
        "• گارانتی 1 ماهه\n\n"
        "لطفاً نوع اپل آیدی مورد نظر خود را انتخاب کنید:",
        reply_markup=buy_service_keyboard()
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
    
    apple_id_type = query.data.split('_')[1]
    price = 200000 if apple_id_type == 'premium' else 100000
    
    user = db.get_user(query.from_user.id)
    if not user or user['balance'] < price:
        keyboard = [
            [InlineKeyboardButton("💳 افزایش موجودی", callback_data='add_funds')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_buy')]
        ]
        await query.message.edit_text(
            "❌ موجودی کافی نیست!\n\n"
            f"💰 موجودی مورد نیاز: {price:,} تومان\n"
            f"💳 موجودی فعلی: {user['balance']:,} تومان\n\n"
            "برای افزایش موجودی کلیک کنید:",
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

    # ایجاد سفارش
    order_id = db.create_order(query.from_user.id, apple_id_type, price)
    
    # ارسال نوتیفیکیشن به ادمین
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data=f'approve_order_{order_id}'),
            InlineKeyboardButton("❌ رد", callback_data=f'reject_order_{order_id}')
        ]
    ]
    
    admin_text = (
        "🛍 سفارش جدید:\n\n"
        f"👤 کاربر: {query.from_user.username}\n"
        f"📦 نوع: {'ویژه' if apple_id_type == 'premium' else 'معمولی'}\n"
        f"💰 مبلغ: {price:,} تومان\n"
        f"🔑 شناسه سفارش: {order_id}"
    )
    
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
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data='back_to_main')]]
    await query.message.edit_text(
        "✅ سفارش شما با موفقیت ثبت شد!\n\n"
        "🕒 در حال بررسی توسط ادمین...\n"
        "پس از تأیید، اطلاعات اپل آیدی ارسال خواهد شد.\n\n"
        f"🔑 کد پیگیری: {order_id}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
