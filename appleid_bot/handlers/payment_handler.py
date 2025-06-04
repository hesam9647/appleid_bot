# apple_id_bot/handlers/payment_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager
import random
import string

db = DatabaseManager()

def generate_payment_id(length=8):
    """تولید شناسه پرداخت تصادفی"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def handle_add_funds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر افزایش موجودی"""
    query = update.callback_query
    await query.answer()
    
    amounts = [
        ("💰 50,000 تومان", "pay_50000"),
        ("💰 100,000 تومان", "pay_100000"),
        ("💰 200,000 تومان", "pay_200000"),
        ("💰 500,000 تومان", "pay_500000")
    ]
    
    keyboard = []
    for text, callback_data in amounts:
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_wallet')])
    
    await query.message.edit_text(
        "💳 افزایش موجودی\n\n"
        "لطفاً مبلغ مورد نظر برای شارژ حساب را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش درخواست پرداخت"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[1])
    payment_id = generate_payment_id()
    
    # ذخیره اطلاعات پرداخت در context
    context.user_data['payment'] = {
        'id': payment_id,
        'amount': amount,
        'status': 'pending'
    }
    
    # اینجا باید به درگاه پرداخت متصل شوید
    # برای مثال، فرض می‌کنیم اطلاعات کارت بانکی را نمایش می‌دهیم
    payment_text = (
        "🏦 اطلاعات واریز:\n\n"
        "🏧 شماره کارت: 6037-9974-1234-5678\n"
        "👤 به نام: نام صاحب کارت\n"
        f"💰 مبلغ: {amount:,} تومان\n"
        f"🔑 کد پیگیری: {payment_id}\n\n"
        "⚠️ پس از واریز، لطفاً دکمه «تایید پرداخت» را بزنید.\n"
        "توجه: حتماً کد پیگیری را در توضیحات واریز ذکر کنید."
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ تایید پرداخت", callback_data=f'verify_payment_{payment_id}')],
        [InlineKeyboardButton("❌ انصراف", callback_data='back_to_wallet')]
    ]
    
    await query.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تایید و بررسی پرداخت"""
    query = update.callback_query
    await query.answer()
    
    payment_id = query.data.split('_')[2]
    payment_info = context.user_data.get('payment')
    
    if not payment_info or payment_info['id'] != payment_id:
        await query.message.edit_text(
            "❌ اطلاعات پرداخت نامعتبر است!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_wallet')
            ]])
        )
        return
    
    # اینجا باید پرداخت را در سیستم خود بررسی کنید
    # برای مثال، فرض می‌کنیم پرداخت در حال بررسی است
    
    await query.message.edit_text(
        "⏳ پرداخت شما در حال بررسی است...\n"
        "پس از تایید، موجودی کیف پول شما به‌روز خواهد شد.\n\n"
        f"🔑 کد پیگیری: {payment_id}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت به منو", callback_data='back_to_main')
        ]])
    )
    
    # ارسال نوتیفیکیشن به ادمین
    try:
        from config.config import ADMIN_IDS
        for admin_id in ADMIN_IDS:
            admin_text = (
                "💰 درخواست شارژ جدید:\n\n"
                f"👤 کاربر: {query.from_user.username}\n"
                f"💳 مبلغ: {payment_info['amount']:,} تومان\n"
                f"🔑 کد پیگیری: {payment_id}"
            )
            admin_keyboard = [[
                InlineKeyboardButton("✅ تایید", callback_data=f'admin_approve_{payment_id}'),
                InlineKeyboardButton("❌ رد", callback_data=f'admin_reject_{payment_id}')
            ]]
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=InlineKeyboardMarkup(admin_keyboard)
            )
    except Exception as e:
        print(f"Error notifying admin: {e}")

async def handle_back_to_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به صفحه کیف پول"""
    query = update.callback_query
    await query.answer()
    
    from handlers.user_handler import handle_wallet
    await handle_wallet(update, context)
