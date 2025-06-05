# apple_id_bot/handlers/help_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش راهنمای ربات"""
    query = update.callback_query
    if query:
        await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📖 راهنمای خرید", callback_data='help_purchase'),
            InlineKeyboardButton("💳 راهنمای پرداخت", callback_data='help_payment')
        ],
        [
            InlineKeyboardButton("❓ سوالات متداول", callback_data='help_faq'),
            InlineKeyboardButton("📜 قوانین", callback_data='help_rules')
        ],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data='back_to_main')]
    ]
    
    help_text = (
        "🔰 راهنمای استفاده از ربات\n\n"
        "به ربات فروش اپل آیدی خوش آمدید!\n"
        "لطفاً بخش مورد نظر خود را انتخاب کنید:"
    )
    
    if query:
        await query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_purchase_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای خرید"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🛍 خرید اپل آیدی", callback_data='buy_service')],
        [InlineKeyboardButton("🔙 بازگشت به راهنما", callback_data='help')]
    ]
    
    help_text = (
        "📖 راهنمای خرید اپل آیدی\n\n"
        "1️⃣ ابتدا از بخش «کیف پول» حساب خود را شارژ کنید\n\n"
        "2️⃣ از منوی اصلی، گزینه «خرید سرویس» را انتخاب کنید\n\n"
        "3️⃣ نوع اپل آیدی مورد نظر خود را انتخاب کنید:\n"
        "   • اپل آیدی معمولی\n"
        "   • اپل آیدی ویژه\n\n"
        "4️⃣ پس از تأیید خرید، اطلاعات اپل آیدی به شما نمایش داده می‌شود\n\n"
        "5️⃣ اطلاعات را در جای امن ذخیره کنید\n\n"
        "⚠️ نکات مهم:\n"
        "• قبل از خرید، حتماً قوانین را مطالعه کنید\n"
        "• در حفظ و نگهداری اطلاعات حساب کاربری دقت کنید\n"
        "• در صورت بروز مشکل، از طریق تیکت اطلاع دهید"
    )
    
    await query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_payment_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای پرداخت"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💰 شارژ کیف پول", callback_data='wallet')],
        [InlineKeyboardButton("🔙 بازگشت به راهنما", callback_data='help')]
    ]
    
    help_text = (
        "💳 راهنمای پرداخت و شارژ کیف پول\n\n"
        "1️⃣ روش‌های پرداخت:\n"
        "   • کارت به کارت\n"
        "   • درگاه پرداخت مستقیم\n\n"
        "2️⃣ مراحل شارژ با کارت به کارت:\n"
        "   • انتخاب مبلغ شارژ\n"
        "   • دریافت شماره کارت و کد پیگیری\n"
        "   • واریز وجه و ثبت کد پیگیری\n"
        "   • تأیید پرداخت توسط ادمین\n\n"
        "3️⃣ مراحل پرداخت با درگاه:\n"
        "   • انتخاب مبلغ شارژ\n"
        "   • هدایت به درگاه پرداخت\n"
        "   • تکمیل فرآیند پرداخت\n"
        "   • شارژ خودکار کیف پول\n\n"
        "⚠️ نکات مهم:\n"
        "• در پرداخت کارت به کارت، حتماً کد پیگیری را در توضیحات ذکر کنید\n"
        "• مبلغ واریزی باید دقیقاً برابر با مبلغ انتخاب شده باشد\n"
        "• پس از واریز، دکمه «تأیید پرداخت» را بزنید"
    )
    
    await query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سوالات متداول"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به راهنما", callback_data='help')]]
    
    faq_text = (
        "❓ سوالات متداول\n\n"
        "س: چقدر طول می‌کشد تا اپل آیدی به دستم برسد؟\n"
        "ج: بلافاصله پس از تأیید پرداخت، اطلاعات اپل آیدی نمایش داده می‌شود.\n\n"
        "س: آیا اپل آیدی‌ها گارانتی دارند؟\n"
        "ج: بله، تمامی اپل آیدی‌ها به مدت یک ماه گارانتی تعویض دارند.\n\n"
        "س: در صورت بروز مشکل چه کنم؟\n"
        "ج: از طریق بخش «تیکت و پشتیبانی» با ما در تماس باشید.\n\n"
        "س: چرا باید از کیف پول استفاده کنم؟\n"
        "ج: برای سرعت و امنیت بیشتر در خرید و امکان استفاده از تخفیف‌ها.\n\n"
        "س: آیا امکان استرداد وجه وجود دارد؟\n"
        "ج: بله، در صورت عدم ارائه سرویس، وجه قابل استرداد است.\n\n"
        "س: چطور می‌توانم از تخفیف‌ها استفاده کنم؟\n"
        "ج: کد تخفیف خود را در بخش «کد هدیه» وارد کنید."
    )
    
    await query.message.edit_text(faq_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قوانین"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به راهنما", callback_data='help')]]
    
    rules_text = (
        "📜 قوانین استفاده از ربات\n\n"
        "1️⃣ خرید و فروش:\n"
        "• تمامی اپل آیدی‌ها اورجینال و دست اول هستند\n"
        "• پس از خرید، مسئولیت حفظ اطلاعات با خریدار است\n"
        "• امکان تعویض فقط در صورت وجود مشکل فنی\n\n"
        "2️⃣ پرداخت و مالی:\n"
        "• تمامی قیمت‌ها به تومان است\n"
        "• وجه واریزی فقط از طریق روش‌های اعلام شده\n"
        "• استرداد وجه طبق شرایط مندرج\n\n"
        "3️⃣ پشتیبانی:\n"
        "• ساعات پاسخگویی: 9 صبح تا 12 شب\n"
        "• حداکثر زمان پاسخگویی به تیکت‌ها: 12 ساعت\n"
        "• ارتباط فقط از طریق ربات\n\n"
        "4️⃣ محدودیت‌ها:\n"
        "• هر کاربر مجاز به داشتن یک حساب است\n"
        "• رعایت ادب و احترام در گفتگوها الزامی است\n"
        "• عدم استفاده از VPN در هنگام خرید\n\n"
        "⚠️ نقض هر یک از قوانین ممکن است منجر به مسدود شدن حساب کاربری شود."
    )
    
    await query.message.edit_text(rules_text, reply_markup=InlineKeyboardMarkup(keyboard))
