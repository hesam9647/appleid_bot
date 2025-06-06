# apple_id_bot/handlers/settings_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from database.db_handler import DatabaseManager
from config.config import ADMIN_IDS
import json

db = DatabaseManager()

# States
WAITING_FOR_TEXT, WAITING_FOR_PRICE = range(2)

async def handle_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تنظیمات ربات"""
    query = update.callback_query
    await query.answer()
    
    settings_text = (
        "⚙️ تنظیمات ربات\n\n"
        "از منوی زیر بخش مورد نظر را انتخاب کنید:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📝 متون ربات", callback_data='edit_texts'),
            InlineKeyboardButton("💰 تنظیم قیمت‌ها", callback_data='edit_prices')
        ],
        [
            InlineKeyboardButton("👥 مدیریت ادمین‌ها", callback_data='manage_admins'),
            InlineKeyboardButton("🔒 تنظیمات امنیتی", callback_data='security_settings')
        ],
        [
            InlineKeyboardButton("📢 تنظیم کانال", callback_data='channel_settings'),
            InlineKeyboardButton("⚙️ سایر تنظیمات", callback_data='other_settings')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    
    await query.message.edit_text(
        settings_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_edit_texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش متون ربات"""
    query = update.callback_query
    await query.answer()
    
    texts = [
        ("👋 پیام خوش‌آمدگویی", "welcome"),
        ("📜 قوانین", "rules"),
        ("❓ سوالات متداول", "faq"),
        ("📝 راهنمای خرید", "purchase_guide"),
        ("💳 راهنمای پرداخت", "payment_guide"),
        ("🎫 راهنمای تیکت", "ticket_guide")
    ]
    
    keyboard = []
    for text, callback in texts:
        keyboard.append([InlineKeyboardButton(text, callback_data=f'edit_text_{callback}')])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_settings')])
    
    await query.message.edit_text(
        "📝 ویرایش متون ربات\n\n"
        "متن مورد نظر برای ویرایش را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ویرایش متن"""
    query = update.callback_query
    await query.answer()
    
    text_type = query.data.split('_')[2]
    context.user_data['editing_text'] = text_type
    
    current_text = db.get_bot_text(text_type)
    
    await query.message.edit_text(
        f"📝 ویرایش متن {text_type}\n\n"
        "متن فعلی:\n"
        f"{current_text}\n\n"
        "متن جدید را ارسال کنید:\n"
        "• می‌توانید از مارک‌داون استفاده کنید\n"
        "• برای لغو، دستور /cancel را بزنید",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_FOR_TEXT

async def save_edited_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره متن ویرایش شده"""
    new_text = update.message.text
    text_type = context.user_data.get('editing_text')
    
    if not text_type:
        await update.message.reply_text("❌ خطا در ویرایش متن!")
        return ConversationHandler.END
    
    # ذخیره متن جدید
    db.update_bot_text(text_type, new_text)
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به تنظیمات", callback_data='back_to_settings')]]
    
    await update.message.reply_text(
        "✅ متن با موفقیت ویرایش شد!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

async def handle_edit_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت قیمت‌ها"""
    query = update.callback_query
    await query.answer()
    
    prices = db.get_prices()
    
    prices_text = (
        "💰 تنظیم قیمت‌ها\n\n"
        "قیمت‌های فعلی:\n\n"
        f"🔰 اپل آیدی معمولی: {prices['normal']:,} تومان\n"
        f"✨ اپل آیدی ویژه: {prices['premium']:,} تومان\n\n"
        "برای تغییر قیمت، گزینه مورد نظر را انتخاب کنید:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔰 قیمت معمولی", callback_data='change_price_normal'),
            InlineKeyboardButton("✨ قیمت ویژه", callback_data='change_price_premium')
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_settings')]
    ]
    
    await query.message.edit_text(
        prices_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_edit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تغییر قیمت"""
    query = update.callback_query
    await query.answer()
    
    price_type = query.data.split('_')[2]
    context.user_data['editing_price'] = price_type
    
    current_price = db.get_prices()[price_type]
    
    await query.message.edit_text(
        f"💰 تغییر قیمت {price_type}\n\n"
        f"قیمت فعلی: {current_price:,} تومان\n\n"
        "قیمت جدید را به تومان وارد کنید:\n"
        "مثال: 100000"
    )
    
    return WAITING_FOR_PRICE

async def save_edited_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره قیمت جدید"""
    try:
        new_price = int(update.message.text)
        if new_price <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "❌ لطفاً یک عدد معتبر وارد کنید!"
        )
        return WAITING_FOR_PRICE
    
    price_type = context.user_data.get('editing_price')
    if not price_type:
        await update.message.reply_text("❌ خطا در تغییر قیمت!")
        return ConversationHandler.END
    
    # ذخیره قیمت جدید
    db.update_price(price_type, new_price)
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به تنظیمات", callback_data='back_to_settings')]]
    
    await update.message.reply_text(
        f"✅ قیمت جدید با موفقیت ذخیره شد!\n\n"
        f"💰 قیمت جدید: {new_price:,} تومان",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

async def handle_manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت ادمین‌ها"""
    query = update.callback_query
    await query.answer()
    
    admins = db.get_admins()
    
    admins_text = "👥 مدیریت ادمین‌ها\n\n"
    keyboard = []
    
    for admin in admins:
        status = "✅ فعال" if admin['is_active'] else "❌ غیرفعال"
        admins_text += f"• {admin['username']} - {status}\n"
        keyboard.append([
            InlineKeyboardButton(
                f"{'❌' if admin['is_active'] else '✅'} {admin['username']}",
                callback_data=f"toggle_admin_{admin['user_id']}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("➕ افزودن ادمین", callback_data='add_admin')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_settings')]
    ])
    
    await query.message.edit_text(
        admins_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_security_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات امنیتی"""
    query = update.callback_query
    await query.answer()
    
    settings = db.get_security_settings()
    
    security_text = (
        "🔒 تنظیمات امنیتی\n\n"
        "وضعیت فعلی:\n\n"
        f"• تأیید دو مرحله‌ای: {'✅' if settings['two_step'] else '❌'}\n"
        f"• محدودیت IP: {'✅' if settings['ip_limit'] else '❌'}\n"
        f"• حداقل موجودی: {settings['min_balance']:,} تومان\n"
        f"• حداکثر برداشت: {settings['max_withdrawal']:,} تومان\n"
        f"• محدودیت تراکنش روزانه: {settings['daily_limit']} عدد"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔐 تأیید دو مرحله‌ای", callback_data='toggle_two_step'),
            InlineKeyboardButton("🌐 محدودیت IP", callback_data='toggle_ip_limit')
        ],
        [
            InlineKeyboardButton("💰 حداقل موجودی", callback_data='set_min_balance'),
            InlineKeyboardButton("💳 حداکثر برداشت", callback_data='set_max_withdrawal')
        ],
        [InlineKeyboardButton("📊 محدودیت تراکنش", callback_data='set_daily_limit')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_settings')]
    ]
    
    await query.message.edit_text(
        security_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_channel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات کانال"""
    query = update.callback_query
    await query.answer()
    
    channels = db.get_channels()
    
    channels_text = "📢 تنظیمات کانال\n\n"
    keyboard = []
    
    if channels:
        channels_text += "کانال‌های فعلی:\n\n"
        for channel in channels:
            status = "✅ فعال" if channel['is_active'] else "❌ غیرفعال"
            channels_text += f"• {channel['username']} - {status}\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"{'❌' if channel['is_active'] else '✅'} {channel['username']}",
                    callback_data=f"toggle_channel_{channel['id']}"
                )
            ])
    else:
        channels_text += "هیچ کانالی تنظیم نشده است!"
    
    keyboard.extend([
        [InlineKeyboardButton("➕ افزودن کانال", callback_data='add_channel')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_settings')]
    ])
    
    await query.message.edit_text(
        channels_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
