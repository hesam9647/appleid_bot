# apple_id_bot/keyboards/admin_keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_main_keyboard() -> InlineKeyboardMarkup:
    """منوی اصلی ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("👥 مدیریت کاربران", callback_data='admin_users'),
            InlineKeyboardButton("🎟 مدیریت اپل آیدی", callback_data='admin_apple_ids')
        ],
        [
            InlineKeyboardButton("💰 گزارش مالی", callback_data='admin_financial'),
            InlineKeyboardButton("📨 پیام همگانی", callback_data='admin_broadcast')
        ],
        [
            InlineKeyboardButton("🎫 مدیریت تیکت‌ها", callback_data='admin_tickets'),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data='admin_settings')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_users_keyboard() -> InlineKeyboardMarkup:
    """منوی مدیریت کاربران"""
    keyboard = [
        [
            InlineKeyboardButton("👥 همه کاربران", callback_data='admin_users_all'),
            InlineKeyboardButton("💰 کاربران خریدار", callback_data='admin_users_buyers')
        ],
        [
            InlineKeyboardButton("🚫 کاربران بلاک", callback_data='admin_users_blocked'),
            InlineKeyboardButton("✨ کاربران ویژه", callback_data='admin_users_vip')
        ],
        [
            InlineKeyboardButton("📊 آمار کاربران", callback_data='admin_users_stats'),
            InlineKeyboardButton("📨 پیام به کاربر", callback_data='admin_user_message')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_apple_ids_keyboard() -> InlineKeyboardMarkup:
    """منوی مدیریت اپل آیدی"""
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن اپل آیدی", callback_data='add_apple_id'),
            InlineKeyboardButton("📋 لیست موجود", callback_data='list_apple_ids')
        ],
        [
            InlineKeyboardButton("💰 تغییر قیمت‌ها", callback_data='change_prices'),
            InlineKeyboardButton("📊 آمار فروش", callback_data='sales_stats')
        ],
        [
            InlineKeyboardButton("🔄 اپل آیدی‌های فروخته شده", callback_data='sold_apple_ids'),
            InlineKeyboardButton("⚠️ گزارش مشکلات", callback_data='apple_id_issues')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_tickets_keyboard() -> InlineKeyboardMarkup:
    """منوی مدیریت تیکت‌ها"""
    keyboard = [
        [
            InlineKeyboardButton("📬 تیکت‌های جدید", callback_data='admin_new_tickets'),
            InlineKeyboardButton("📝 در حال بررسی", callback_data='admin_pending_tickets')
        ],
        [
            InlineKeyboardButton("✅ تیکت‌های پاسخ داده شده", callback_data='admin_answered_tickets'),
            InlineKeyboardButton("📊 آمار تیکت‌ها", callback_data='admin_ticket_stats')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_financial_keyboard() -> InlineKeyboardMarkup:
    """منوی گزارش مالی"""
    keyboard = [
        [
            InlineKeyboardButton("📊 گزارش امروز", callback_data='admin_today_report'),
            InlineKeyboardButton("📈 گزارش این ماه", callback_data='admin_month_report')
        ],
        [
            InlineKeyboardButton("💰 تراکنش‌های اخیر", callback_data='admin_recent_transactions'),
            InlineKeyboardButton("📑 گزارش سفارشی", callback_data='admin_custom_report')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_settings_keyboard() -> InlineKeyboardMarkup:
    """منوی تنظیمات"""
    keyboard = [
        [
            InlineKeyboardButton("📝 ویرایش متون", callback_data='admin_edit_texts'),
            InlineKeyboardButton("💰 تنظیم قیمت‌ها", callback_data='admin_set_prices')
        ],
        [
            InlineKeyboardButton("👥 مدیریت ادمین‌ها", callback_data='admin_manage_admins'),
            InlineKeyboardButton("🔒 تنظیمات امنیتی", callback_data='admin_security')
        ],
        [
            InlineKeyboardButton("📢 تنظیمات کانال", callback_data='admin_channel_settings'),
            InlineKeyboardButton("⚙️ سایر تنظیمات", callback_data='admin_other_settings')
        ],
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data='back_to_admin')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام همگانی"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📨 ارسال به همه", callback_data='broadcast_all'),
            InlineKeyboardButton("📌 ارسال به خریداران", callback_data='broadcast_buyers')
        ],
        [
            InlineKeyboardButton("✨ ارسال به ویژه‌ها", callback_data='broadcast_vip'),
            InlineKeyboardButton("💬 ارسال به فعال‌ها", callback_data='broadcast_active')
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')]
    ]
    
    await query.message.edit_text(
        "📨 ارسال پیام همگانی\n\n"
        "👈 گروه هدف را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_admin_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تیکت‌ها"""
    query = update.callback_query
    await query.answer()
    
    # دریافت آمار تیکت‌ها
    ticket_stats = db.get_ticket_stats()
    
    tickets_text = (
        "🎫 مدیریت تیکت‌ها\n\n"
        "📊 آمار تیکت‌ها:\n"
        f"• جدید: {ticket_stats['new']} عدد\n"
        f"• در حال بررسی: {ticket_stats['pending']} عدد\n"
        f"• پاسخ داده شده: {ticket_stats['answered']} عدد\n"
        f"• بسته شده: {ticket_stats['closed']} عدد\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    await query.message.edit_text(
        tickets_text,
        reply_markup=admin_tickets_keyboard()
    )

async def handle_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات ربات"""
    query = update.callback_query
    await query.answer()
    
    settings_text = (
        "⚙️ تنظیمات ربات\n\n"
        "• ویرایش متون ربات\n"
        "• تنظیم قیمت‌ها\n"
        "• مدیریت ادمین‌ها\n"
        "• تنظیمات امنیتی\n"
        "• تنظیمات کانال\n"
        "• سایر تنظیمات\n\n"
        "🔰 از منوی زیر انتخاب کنید:"
    )
    
    await query.message.edit_text(
        settings_text,
        reply_markup=admin_settings_keyboard()
    )

async def handle_user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربر خاص"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    user = db.get_user_details(user_id)
    
    if not user:
        await query.message.edit_text(
            "❌ کاربر یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='admin_users')
            ]])
        )
        return
    
    user_text = (
        f"👤 مدیریت کاربر {user['username']}\n\n"
        f"🆔 شناسه: {user['user_id']}\n"
        f"💰 موجودی: {user['balance']:,} تومان\n"
        f"📦 تعداد خرید: {user['purchases_count']} عدد\n"
        f"💳 مجموع خرید: {user['total_purchase_amount']:,} تومان\n"
        f"📅 تاریخ عضویت: {user['created_at']}\n"
        f"⭐️ وضعیت: {'فعال' if user['is_active'] else 'غیرفعال'}\n"
        f"🚫 وضعیت بلاک: {'بله' if user['is_blocked'] else 'خیر'}\n\n"
        "📝 یادداشت ادمین:\n"
        f"{user['admin_note'] or 'بدون یادداشت'}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🚫 بلاک" if not user['is_blocked'] else "✅ آنبلاک",
                callback_data=f"toggle_block_{user_id}"
            ),
            InlineKeyboardButton("💰 تغییر موجودی", callback_data=f"change_balance_{user_id}")
        ],
        [
            InlineKeyboardButton("📝 افزودن یادداشت", callback_data=f"add_note_{user_id}"),
            InlineKeyboardButton("📨 ارسال پیام", callback_data=f"send_message_{user_id}")
        ],
        [
            InlineKeyboardButton("📋 سوابق خرید", callback_data=f"user_purchases_{user_id}"),
            InlineKeyboardButton("💳 سوابق مالی", callback_data=f"user_transactions_{user_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='admin_users')]
    ]
    
    await query.message.edit_text(
        user_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_apple_id_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت اپل آیدی خاص"""
    query = update.callback_query
    await query.answer()
    
    apple_id_id = int(query.data.split('_')[2])
    apple_id = db.get_apple_id_details(apple_id_id)
    
    if not apple_id:
        await query.message.edit_text(
            "❌ اپل آیدی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='admin_apple_ids')
            ]])
        )
        return
    
    apple_id_text = (
        "🎟 اطلاعات اپل آیدی\n\n"
        f"📧 ایمیل: {apple_id['email']}\n"
        f"🔐 رمز عبور: {apple_id['password']}\n"
        f"📨 رمز ایمیل: {apple_id['email_password']}\n"
        f"📅 تاریخ تولد: {apple_id['birth_date']}\n\n"
        "❓ سوالات امنیتی:\n"
        f"1️⃣ {apple_id['security_q1']}\n"
        f"↪️ {apple_id['security_a1']}\n\n"
        f"2️⃣ {apple_id['security_q2']}\n"
        f"↪️ {apple_id['security_a2']}\n\n"
        f"3️⃣ {apple_id['security_q3']}\n"
        f"↪️ {apple_id['security_a3']}\n\n"
        f"📊 وضعیت: {apple_id['status']}\n"
        f"💰 قیمت: {apple_id['price']:,} تومان\n"
        f"📅 تاریخ ثبت: {apple_id['created_at']}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_apple_id_{apple_id_id}"),
            InlineKeyboardButton("❌ حذف", callback_data=f"delete_apple_id_{apple_id_id}")
        ],
        [
            InlineKeyboardButton("💰 تغییر قیمت", callback_data=f"change_price_{apple_id_id}"),
            InlineKeyboardButton("📊 تغییر وضعیت", callback_data=f"change_status_{apple_id_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='admin_apple_ids')]
    ]
    
    await query.message.edit_text(
        apple_id_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
