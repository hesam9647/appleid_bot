# apple_id_bot/handlers/payment_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ContextTypes
from database.db_handler import DatabaseManager
from config.config import PAYMENT_METHODS, ADMIN_IDS
import datetime
import random
import string

db = DatabaseManager()

def generate_payment_id():
    """تولید شناسه پرداخت منحصر به فرد"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def handle_add_funds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر افزایش موجودی"""
    query = update.callback_query
    await query.answer()
    
    payment_text = (
        "💳 افزایش موجودی کیف پول\n\n"
        "💡 روش‌های پرداخت:\n"
        "• کارت به کارت\n"
        "• درگاه مستقیم\n"
        "• پرداخت ارزی\n\n"
        "👈 لطفاً مبلغ مورد نظر را انتخاب کنید:"
    )
    
    amounts = [
        ("💰 50,000 تومان", "50000"),
        ("💰 100,000 تومان", "100000"),
        ("💰 200,000 تومان", "200000"),
        ("💰 500,000 تومان", "500000"),
        ("💰 1,000,000 تومان", "1000000")
    ]
    
    keyboard = []
    for text, amount in amounts:
        keyboard.append([InlineKeyboardButton(text, callback_data=f'select_amount_{amount}')])
    
    keyboard.append([InlineKeyboardButton("💱 مبلغ دلخواه", callback_data='custom_amount')])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_wallet')])
    
    await query.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب روش پرداخت"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[2])
    context.user_data['payment_amount'] = amount
    
    keyboard = [
        [InlineKeyboardButton("💳 کارت به کارت", callback_data=f'pay_card_{amount}')],
        [InlineKeyboardButton("🏦 درگاه مستقیم", callback_data=f'pay_gateway_{amount}')],
        [InlineKeyboardButton("💱 پرداخت ارزی", callback_data=f'pay_crypto_{amount}')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_add_funds')]
    ]
    
    await query.message.edit_text(
        f"💳 انتخاب روش پرداخت\n\n"
        f"💰 مبلغ: {amount:,} تومان\n\n"
        "👈 لطفاً روش پرداخت را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_card_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پرداخت با کارت به کارت"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[2])
    payment_id = generate_payment_id()
    
    # ذخیره اطلاعات پرداخت
    db.create_payment(
        user_id=query.from_user.id,
        amount=amount,
        payment_id=payment_id,
        method='card'
    )
    
    card_info = PAYMENT_METHODS['card']
    
    payment_text = (
        "💳 پرداخت کارت به کارت\n\n"
        f"💰 مبلغ: {amount:,} تومان\n"
        f"🏦 شماره کارت: `{card_info['number']}`\n"
        f"👤 به نام: {card_info['name']}\n"
        f"🏛 بانک: {card_info['bank']}\n"
        f"🔑 کد پیگیری: `{payment_id}`\n\n"
        "⚠️ نکات مهم:\n"
        "• لطفاً دقیقاً مبلغ ذکر شده را واریز کنید\n"
        "• کد پیگیری را در توضیحات تراکنش وارد کنید\n"
        "• پس از واریز، رسید پرداخت را ارسال کنید\n"
        "• واریز از کارت شخصی انجام شود"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 کپی شماره کارت", callback_data=f'copy_{card_info["number"]}')],
        [InlineKeyboardButton("📸 ارسال رسید پرداخت", callback_data=f'send_receipt_{payment_id}')],
        [InlineKeyboardButton("❌ انصراف", callback_data='back_to_wallet')]
    ]
    
    await query.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_gateway_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پرداخت با درگاه مستقیم"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[2])
    payment_id = generate_payment_id()
    
    # ذخیره اطلاعات پرداخت
    db.create_payment(
        user_id=query.from_user.id,
        amount=amount,
        payment_id=payment_id,
        method='gateway'
    )
    
    # در اینجا باید به درگاه پرداخت متصل شوید
    payment_link = f"https://your-payment-gateway.com/pay/{payment_id}/{amount}"
    
    payment_text = (
        "🏦 پرداخت از طریق درگاه\n\n"
        f"💰 مبلغ: {amount:,} تومان\n"
        f"🔑 کد پیگیری: {payment_id}\n\n"
        "⚠️ نکات مهم:\n"
        "• پس از کلیک روی دکمه پرداخت، به درگاه بانکی متصل می‌شوید\n"
        "• پس از پرداخت موفق، کیف پول شما به صورت خودکار شارژ می‌شود\n"
        "• در صورت بروز مشکل، از طریق تیکت اطلاع دهید"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 پرداخت آنلاین", url=payment_link)],
        [InlineKeyboardButton("✅ تأیید پرداخت", callback_data=f'verify_gateway_{payment_id}')],
        [InlineKeyboardButton("❌ انصراف", callback_data='back_to_wallet')]
    ]
    
    await query.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پرداخت با ارز دیجیتال"""
    query = update.callback_query
    await query.answer()
    
    amount = int(query.data.split('_')[2])
    payment_id = generate_payment_id()
    
    # تبدیل مبلغ به دلار و USDT
    usd_amount = round(amount / 50000, 2)  # نرخ تبدیل فرضی
    
    # ذخیره اطلاعات پرداخت
    db.create_payment(
        user_id=query.from_user.id,
        amount=amount,
        payment_id=payment_id,
        method='crypto'
    )
    
    crypto_info = PAYMENT_METHODS['crypto']
    
    payment_text = (
        "💱 پرداخت ارزی\n\n"
        f"💰 مبلغ: {amount:,} تومان\n"
        f"💵 معادل: {usd_amount} USDT\n"
        f"🔑 کد پیگیری: {payment_id}\n\n"
        "🏦 آدرس‌های واریز:\n\n"
        f"• USDT (TRC20):\n`{crypto_info['trc20']}`\n\n"
        f"• USDT (ERC20):\n`{crypto_info['erc20']}`\n\n"
        "⚠️ نکات مهم:\n"
        "• لطفاً دقیقاً مبلغ ذکر شده را واریز کنید\n"
        "• پس از واریز، تصویر تراکنش را ارسال کنید\n"
        "• شبکه انتقال را درست انتخاب کنید"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📱 کپی TRC20", callback_data=f'copy_{crypto_info["trc20"]}'),
            InlineKeyboardButton("📱 کپی ERC20", callback_data=f'copy_{crypto_info["erc20"]}')
        ],
        [InlineKeyboardButton("📸 ارسال رسید تراکنش", callback_data=f'send_crypto_receipt_{payment_id}')],
        [InlineKeyboardButton("❌ انصراف", callback_data='back_to_wallet')]
    ]
    
    await query.message.edit_text(
        payment_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت رسید پرداخت"""
    message = update.message
    payment_id = context.user_data.get('active_payment_id')
    
    if not payment_id:
        await message.reply_text(
            "❌ خطا در ثبت رسید!\n"
            "لطفاً دوباره از منوی کیف پول اقدام کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت به کیف پول", callback_data='back_to_wallet')
            ]])
        )
        return
    
    # ذخیره رسید در دیتابیس
    db.update_payment_receipt(payment_id, message.photo[-1].file_id if message.photo else message.text)
    
    # ارسال به ادمین‌ها
    payment_info = db.get_payment(payment_id)
    
    admin_text = (
        "💳 رسید پرداخت جدید\n\n"
        f"👤 کاربر: {message.from_user.username}\n"
        f"💰 مبلغ: {payment_info['amount']:,} تومان\n"
        f"🔑 کد پیگیری: {payment_id}\n"
        f"📅 تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data=f'approve_payment_{payment_id}'),
            InlineKeyboardButton("❌ رد", callback_data=f'reject_payment_{payment_id}')
        ]
    ]
    
    for admin_id in ADMIN_IDS:
        try:
            if message.photo:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=message.photo[-1].file_id,
                    caption=admin_text,
                    reply_markup=InlineKeyboardMarkup(admin_keyboard)
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"{admin_text}\n\nرسید متنی:\n{message.text}",
                    reply_markup=InlineKeyboardMarkup(admin_keyboard)
                )
        except Exception as e:
            print(f"Error notifying admin {admin_id}: {e}")
    
    await message.reply_text(
        "✅ رسید پرداخت شما با موفقیت ثبت شد\n"
        "پس از تأیید ادمین، کیف پول شما شارژ خواهد شد.\n\n"
        f"🔑 کد پیگیری: {payment_id}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت به کیف پول", callback_data='back_to_wallet')
        ]])
    )
