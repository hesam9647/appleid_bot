# apple_id_bot/handlers/admin_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db_handler import DatabaseManager
from config.config import ADMIN_IDS
import json
from typing import Dict, List

db = DatabaseManager()

# States for conversation
WAITING_FOR_EMAIL, WAITING_FOR_PASSWORD, WAITING_FOR_EMAIL_PASS, \
WAITING_FOR_BIRTH, WAITING_FOR_SECURITY_Q1, WAITING_FOR_SECURITY_A1, \
WAITING_FOR_SECURITY_Q2, WAITING_FOR_SECURITY_A2, \
WAITING_FOR_SECURITY_Q3, WAITING_FOR_SECURITY_A3, \
WAITING_FOR_BROADCAST, WAITING_FOR_USER_NOTE = range(12)

def is_admin(user_id: int) -> bool:
    """چک کردن ادمین بودن کاربر"""
    return user_id in ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل اصلی ادمین"""
    if not is_admin(update.effective_user.id):
        return
    
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
    
    text = "🔰 پنل مدیریت\n\nخوش آمدید. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران"""
    query = update.callback_query
    await query.answer()
    
    users = db.get_all_users()
    keyboard = []
    
    # فیلترهای کاربران
    keyboard.append([
        InlineKeyboardButton("👥 همه", callback_data='filter_all'),
        InlineKeyboardButton("🚫 بلاک شده", callback_data='filter_blocked'),
        InlineKeyboardButton("💰 خریداران", callback_data='filter_buyers')
    ])
    
    # لیست کاربران
    for user in users[:5]:  # نمایش 5 کاربر اول
        status = "🚫" if user['is_blocked'] else "✅"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {user['username']} - موجودی: {user['balance']:,}",
                callback_data=f"user_{user['user_id']}"
            )
        ])
    
    # دکمه‌های ناوبری
    keyboard.append([
        InlineKeyboardButton("⬅️ قبلی", callback_data='prev_users'),
        InlineKeyboardButton("➡️ بعدی", callback_data='next_users')
    ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')])
    
    await query.message.edit_text(
        "👥 مدیریت کاربران\n\n"
        "• برای مدیریت هر کاربر، روی نام آن کلیک کنید\n"
        "• از فیلترها برای مرتب‌سازی استفاده کنید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربر خاص"""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[1])
    user = db.get_user(user_id)
    
    if not user:
        await query.message.edit_text(
            "❌ کاربر یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='admin_users')
            ]])
        )
        return
    
    status = "🚫 بلاک شده" if user['is_blocked'] else "✅ فعال"
    keyboard = [
        [
            InlineKeyboardButton(
                "🚫 بلاک" if not user['is_blocked'] else "✅ آنبلاک",
                callback_data=f"toggle_block_{user_id}"
            ),
            InlineKeyboardButton("💰 افزایش موجودی", callback_data=f"add_balance_{user_id}")
        ],
        [
            InlineKeyboardButton("📝 یادداشت", callback_data=f"add_note_{user_id}"),
            InlineKeyboardButton("📨 ارسال پیام", callback_data=f"send_message_{user_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='admin_users')]
    ]
    
    text = (
        f"👤 مدیریت کاربر\n\n"
        f"🆔 شناسه: {user_id}\n"
        f"👤 نام کاربری: {user['username']}\n"
        f"💰 موجودی: {user['balance']:,} تومان\n"
        f"⭐️ وضعیت: {status}\n"
        f"📅 تاریخ عضویت: {user['created_at']}\n"
    )
    
    if user.get('note'):
        text += f"\n📝 یادداشت:\n{user['note']}"
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def add_apple_id_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند افزودن اپل آیدی"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['apple_id'] = {}
    
    await query.message.edit_text(
        "🍎 افزودن اپل آیدی جدید\n\n"
        "لطفاً ایمیل اپل آیدی را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 انصراف", callback_data='admin_apple_ids')
        ]])
    )
    
    return WAITING_FOR_EMAIL

async def add_apple_id_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت ایمیل اپل آیدی"""
    context.user_data['apple_id']['email'] = update.message.text
    
    await update.message.reply_text(
        "✅ ایمیل ذخیره شد\n\n"
        "حالا لطفاً رمز اپل آیدی را وارد کنید:"
    )
    
    return WAITING_FOR_PASSWORD

# ادامه توابع مربوط به دریافت اطلاعات اپل آیدی...

async def save_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره نهایی اپل آیدی"""
    apple_id_data = context.user_data['apple_id']
    
    success = db.add_apple_id(apple_id_data)
    
    if success:
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data='admin_apple_ids')]]
        await update.message.reply_text(
            "✅ اپل آیدی با موفقیت ذخیره شد!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("❌ خطا در ذخیره اپل آیدی!")
    
    return ConversationHandler.END

# apple_id_bot/handlers/admin_handler.py

# اضافه کردن به بقیه imports

async def manage_apple_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت اپل آیدی‌ها"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن اپل آیدی", callback_data='add_apple_id'),
            InlineKeyboardButton("📋 لیست موجود", callback_data='list_apple_ids')
        ],
        [
            InlineKeyboardButton("🔄 تغییر قیمت‌ها", callback_data='change_prices'),
            InlineKeyboardButton("📊 آمار فروش", callback_data='apple_id_stats')
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_admin')]
    ]
    
    await query.message.edit_text(
        "🎟 مدیریت اپل آیدی‌ها\n\n"
        "• برای افزودن اپل آیدی جدید، گزینه «افزودن» را انتخاب کنید\n"
        "• برای مشاهده و مدیریت اپل آیدی‌های موجود، گزینه «لیست» را انتخاب کنید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def list_apple_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست اپل آیدی‌ها"""
    query = update.callback_query
    await query.answer()
    
    apple_ids = db.get_apple_ids()
    
    if not apple_ids:
        keyboard = [
            [InlineKeyboardButton("➕ افزودن اپل آیدی", callback_data='add_apple_id')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='admin_apple_ids')]
        ]
        await query.message.edit_text(
            "❌ هیچ اپل آیدی‌ای موجود نیست!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    keyboard = []
    for apple_id in apple_ids[:5]:  # نمایش 5 مورد اول
        status = "🟢" if apple_id['status'] == 'available' else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {apple_id['email']} - {apple_id['type']}",
                callback_data=f"apple_id_{apple_id['id']}"
            )
        ])
    
    # دکمه‌های ناوبری
    keyboard.append([
        InlineKeyboardButton("⬅️ قبلی", callback_data='prev_apple_ids'),
        InlineKeyboardButton("➡️ بعدی", callback_data='next_apple_ids')
    ])
    
    keyboard.append([
        InlineKeyboardButton("➕ افزودن", callback_data='add_apple_id'),
        InlineKeyboardButton("🔙 بازگشت", callback_data='admin_apple_ids')
    ])
    
    await query.message.edit_text(
        "📋 لیست اپل آیدی‌ها\n\n"
        "🟢 موجود | 🔴 فروخته شده\n"
        "برای مدیریت هر اپل آیدی، روی آن کلیک کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def manage_single_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت یک اپل آیدی خاص"""
    query = update.callback_query
    await query.answer()
    
    apple_id_id = int(query.data.split('_')[2])
    apple_id = db.get_apple_id(apple_id_id)
    
    if not apple_id:
        await query.message.edit_text(
            "❌ اپل آیدی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data='list_apple_ids')
            ]])
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("❌ حذف", callback_data=f"delete_apple_id_{apple_id_id}"),
            InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_apple_id_{apple_id_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='list_apple_ids')]
    ]
    
    text = (
        f"🎟 اطلاعات اپل آیدی\n\n"
        f"📧 ایمیل: {apple_id['email']}\n"
        f"🔐 رمز: {apple_id['password']}\n"
        f"📨 رمز ایمیل: {apple_id['email_password']}\n"
        f"📅 تاریخ تولد: {apple_id['birth_date']}\n\n"
        f"❓ سوالات امنیتی:\n"
        f"1️⃣ {apple_id['security_q1']}\n"
        f"↪️ {apple_id['security_a1']}\n\n"
        f"2️⃣ {apple_id['security_q2']}\n"
        f"↪️ {apple_id['security_a2']}\n\n"
        f"3️⃣ {apple_id['security_q3']}\n"
        f"↪️ {apple_id['security_a3']}\n\n"
        f"📊 وضعیت: {'موجود' if apple_id['status'] == 'available' else 'فروخته شده'}"
    )
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# اضافه کردن به DatabaseManager در database/db_handler.py:

def get_apple_ids(self) -> List[Dict]:
    """دریافت لیست همه اپل آیدی‌ها"""
    self.cursor.execute("""
        SELECT id, email, status, type FROM apple_ids
        ORDER BY created_at DESC
    """)
    apple_ids = self.cursor.fetchall()
    return [{
        'id': a[0],
        'email': a[1],
        'status': a[2],
        'type': a[3]
    } for a in apple_ids]

def get_apple_id(self, apple_id_id: int) -> Dict:
    """دریافت اطلاعات یک اپل آیدی خاص"""
    self.cursor.execute("""
        SELECT * FROM apple_ids WHERE id = ?
    """, (apple_id_id,))
    a = self.cursor.fetchone()
    if a:
        return {
            'id': a[0],
            'email': a[1],
            'password': a[2],
            'email_password': a[3],
            'birth_date': a[4],
            'security_q1': a[5],
            'security_a1': a[6],
            'security_q2': a[7],
            'security_a2': a[8],
            'security_q3': a[9],
            'security_a3': a[10],
            'status': a[11],
            'type': a[12]
        }
    return None

# apple_id_bot/handlers/admin_handler.py

# اضافه کردن به بقیه کد قبلی...

async def add_apple_id_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت رمز اپل آیدی"""
    context.user_data['apple_id']['password'] = update.message.text
    
    await update.message.reply_text(
        "✅ رمز اپل آیدی ذخیره شد\n\n"
        "حالا لطفاً رمز ایمیل را وارد کنید:"
    )
    
    return WAITING_FOR_EMAIL_PASS

async def add_apple_id_email_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت رمز ایمیل"""
    context.user_data['apple_id']['email_password'] = update.message.text
    
    await update.message.reply_text(
        "✅ رمز ایمیل ذخیره شد\n\n"
        "حالا لطفاً تاریخ تولد را به فرمت YYYY/MM/DD وارد کنید:"
    )
    
    return WAITING_FOR_BIRTH

async def add_apple_id_birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت تاریخ تولد"""
    context.user_data['apple_id']['birth_date'] = update.message.text
    
    await update.message.reply_text(
        "✅ تاریخ تولد ذخیره شد\n\n"
        "حالا لطفاً سوال امنیتی اول را وارد کنید:"
    )
    
    return WAITING_FOR_SECURITY_Q1

async def add_apple_id_security_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سوال امنیتی اول"""
    context.user_data['apple_id']['security_q1'] = update.message.text
    
    await update.message.reply_text(
        "✅ سوال اول ذخیره شد\n\n"
        "حالا لطفاً پاسخ سوال اول را وارد کنید:"
    )
    
    return WAITING_FOR_SECURITY_A1

async def add_apple_id_security_a1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پاسخ سوال امنیتی اول"""
    context.user_data['apple_id']['security_a1'] = update.message.text
    
    await update.message.reply_text(
        "✅ پاسخ اول ذخیره شد\n\n"
        "حالا لطفاً سوال امنیتی دوم را وارد کنید:"
    )
    
    return WAITING_FOR_SECURITY_Q2

async def add_apple_id_security_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سوال امنیتی دوم"""
    context.user_data['apple_id']['security_q2'] = update.message.text
    
    await update.message.reply_text(
        "✅ سوال دوم ذخیره شد\n\n"
        "حالا لطفاً پاسخ سوال دوم را وارد کنید:"
    )
    
    return WAITING_FOR_SECURITY_A2

async def add_apple_id_security_a2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پاسخ سوال امنیتی دوم"""
    context.user_data['apple_id']['security_a2'] = update.message.text
    
    await update.message.reply_text(
        "✅ پاسخ دوم ذخیره شد\n\n"
        "حالا لطفاً سوال امنیتی سوم را وارد کنید:"
    )
    
    return WAITING_FOR_SECURITY_Q3

async def add_apple_id_security_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سوال امنیتی سوم"""
    context.user_data['apple_id']['security_q3'] = update.message.text
    
    await update.message.reply_text(
        "✅ سوال سوم ذخیره شد\n\n"
        "حالا لطفاً پاسخ سوال سوم را وارد کنید:"
    )
    
    return WAITING_FOR_SECURITY_A3

async def add_apple_id_security_a3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پاسخ سوال امنیتی سوم و ذخیره نهایی"""
    context.user_data['apple_id']['security_a3'] = update.message.text
    apple_id_data = context.user_data['apple_id']
    
    # نمایش پیش‌نمایش اطلاعات
    preview_text = (
        "📝 پیش‌نمایش اطلاعات اپل آیدی:\n\n"
        f"📧 ایمیل: {apple_id_data['email']}\n"
        f"🔐 رمز اپل آیدی: {apple_id_data['password']}\n"
        f"🔑 رمز ایمیل: {apple_id_data['email_password']}\n"
        f"📅 تاریخ تولد: {apple_id_data['birth_date']}\n\n"
        "❓ سوالات امنیتی:\n"
        f"1️⃣ {apple_id_data['security_q1']}\n"
        f"↪️ {apple_id_data['security_a1']}\n\n"
        f"2️⃣ {apple_id_data['security_q2']}\n"
        f"↪️ {apple_id_data['security_a2']}\n\n"
        f"3️⃣ {apple_id_data['security_q3']}\n"
        f"↪️ {apple_id_data['security_a3']}\n\n"
        "آیا اطلاعات فوق را تأیید می‌کنید؟"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید و ذخیره", callback_data='confirm_apple_id'),
            InlineKeyboardButton("❌ انصراف", callback_data='cancel_apple_id')
        ]
    ]
    
    await update.message.reply_text(
        preview_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

async def confirm_apple_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید و ذخیره نهایی اپل آیدی"""
    query = update.callback_query
    await query.answer()
    
    apple_id_data = context.user_data.get('apple_id')
    if not apple_id_data:
        await query.message.edit_text("❌ خطا: اطلاعات اپل آیدی یافت نشد!")
        return
    
    success = db.add_apple_id(apple_id_data)
    
    if success:
        await query.message.edit_text(
            "✅ اپل آیدی با موفقیت ذخیره شد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت به مدیریت", callback_data='admin_apple_ids')
            ]])
        )
    else:
        await query.message.edit_text(
            "❌ خطا در ذخیره اپل آیدی!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 تلاش مجدد", callback_data='add_apple_id')
            ]])
        )

async def handle_payment_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر تأیید پرداخت توسط ادمین"""
    query = update.callback_query
    await query.answer()
    
    action, payment_id = query.data.split('_')[1:]
    payment_info = db.get_payment(payment_id)
    
    if not payment_info:
        await query.message.edit_text("❌ اطلاعات پرداخت یافت نشد!")
        return
    
    if action == 'approve':
        # افزایش موجودی کاربر
        success = db.update_balance(payment_info['user_id'], payment_info['amount'])
        if success:
            # ارسال پیام به کاربر
            try:
                await context.bot.send_message(
                    chat_id=payment_info['user_id'],
                    text=f"✅ پرداخت شما تأیید شد!\n\n"
                         f"💰 مبلغ: {payment_info['amount']:,} تومان\n"
                         f"🔑 کد پیگیری: {payment_id}\n\n"
                         "موجودی کیف پول شما به‌روز شد."
                )
            except Exception as e:
                print(f"Error notifying user: {e}")
            
            await query.message.edit_text(
                f"✅ پرداخت با کد {payment_id} تأیید شد."
            )
        else:
            await query.message.edit_text("❌ خطا در به‌روزرسانی موجودی!")
    
    elif action == 'reject':
        # ارسال پیام به کاربر
        try:
            await context.bot.send_message(
                chat_id=payment_info['user_id'],
                text=f"❌ پرداخت شما تأیید نشد!\n\n"
                     f"🔑 کد پیگیری: {payment_id}\n\n"
                     "لطفاً با پشتیبانی تماس بگیرید."
            )
        except Exception as e:
            print(f"Error notifying user: {e}")
        
        await query.message.edit_text(
            f"❌ پرداخت با کد {payment_id} رد شد."
        )

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه‌های بازگشت"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == 'back_to_main':
        from keyboards.user_keyboards import main_menu_keyboard
        await query.message.edit_text(
            "به ربات فروش اپل آیدی خوش آمدید!",
            reply_markup=main_menu_keyboard()
        )
    
    elif callback_data == 'back_to_admin':
        from keyboards.admin_keyboards import admin_main_keyboard
        await query.message.edit_text(
            "🔰 پنل مدیریت\n\nخوش آمدید. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=admin_main_keyboard()
        )
    
    elif callback_data == 'back_to_buy':
        from keyboards.user_keyboards import buy_service_keyboard
        await query.message.edit_text(
            "🛍 فروشگاه اپل آیدی\n\n"
            "لطفاً نوع اپل آیدی مورد نظر خود را انتخاب کنید:",
            reply_markup=buy_service_keyboard()
        )
