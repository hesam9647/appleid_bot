import telebot
from telebot import types
import pandas as pd
import io
from config import TOKEN, ADMIN_IDS
import database as db

# ابتدا پایگاه داده را مقداردهی اولیه می‌کنیم
db.init_db()

bot = telebot.TeleBot(TOKEN)

# وضعیت‌های کاربر
user_states = {}

# بررسی ادمین بودن
def is_admin(user_id):
    return user_id in ADMIN_IDS

# منوهای کاربر و ادمین
def user_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('مشاهده سرویس‌های خرید شده', 'خرید سرویس')
    markup.row('تعرفه‌ها', 'کیف پول و موجودی', 'ارتقاء موجودی')
    markup.row('تیکت و پشتیبانی', 'راهنما', 'قوانین')
    bot.send_message(chat_id, "به ربات خوش آمدید. لطفاً یکی از گزینه‌ها را انتخاب کنید.", reply_markup=markup)

def admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('گزارش‌های فروش', 'ارسال پیام به کاربران')
    markup.row('مدیریت کاربران', 'مدیریت درخواست‌های افزایش موجودی')
    markup.row('اپلیکیشن آی‌دی', 'وضعیت خرید سرویس')
    markup.row('مدیریت قوانین', 'راهنما')
    bot.send_message(chat_id, "پنل ادمین", reply_markup=markup)

# شروع
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    if is_admin(user_id):
        admin_menu(message.chat.id)
    else:
        user_menu(message.chat.id)

# مدیریت پیام‌های عمومی و حالت‌های خاص
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id)

    # بررسی حالت‌های خاص
    if state:
        action = state.get('action')
        if action == 'broadcast':
            send_broadcast(text)
            bot.send_message(chat_id, "پیام به تمامی کاربران ارسال شد.")
            user_states.pop(chat_id)
            return
        elif action == 'upload_excel':
            handle_excel_upload(message)
            return
        elif action == 'edit_rules':
            db.set_setting('rules', text)
            bot.send_message(chat_id, "قوانین بروزرسانی شد.")
            user_states.pop(chat_id)
            return
        elif action == 'create_ticket':
            create_ticket(chat_id, text)
            user_states.pop(chat_id)
            return
        elif action == 'charge_wallet_method':
            handle_wallet_charge_method(chat_id, text)
            return
        elif action == 'charge_amount':
            handle_wallet_amount(chat_id, text)
            return
        elif action == 'charge_card':
            handle_card_image(chat_id, message)
            return

    # در صورت نبود حالت خاص، دستورات عادی
    if is_admin(message.from_user.id):
        handle_admin_commands(message, text)
    else:
        handle_user_commands(message, text)

# دستورات ادمین
def handle_admin_commands(message, text):
    chat_id = message.chat.id
    if text == 'گزارش‌های فروش':
        report = generate_sales_report()
        bot.send_message(chat_id, report)
    elif text == 'ارسال پیام به کاربران':
        user_states[chat_id] = {'action': 'broadcast'}
        bot.send_message(chat_id, "پیام خود را برای ارسال به تمامی کاربران وارد کنید.")
    elif text == 'مدیریت کاربران':
        manage_users(chat_id)
    elif text == 'مدیریت درخواست‌های افزایش موجودی':
        handle_topup_requests(chat_id)
    elif text == 'اپلیکیشن آی‌دی':
        bot.send_message(chat_id, "لطفاً فایل اکسل حاوی اپل آیدی‌ها را ارسال کنید.")
        user_states[chat_id] = {'action': 'upload_excel'}
    elif text == 'وضعیت خرید سرویس':
        toggle_service_status(chat_id)
    elif text == 'مدیریت قوانین':
        bot.send_message(chat_id, "لطفاً متن قوانین جدید را ارسال کنید.")
        user_states[chat_id] = {'action': 'edit_rules'}
    elif text == 'راهنما':
        show_help(chat_id)
    else:
        bot.send_message(chat_id, "دستور نامشخص است.")

# دستورات کاربر
def handle_user_commands(message, text):
    chat_id = message.chat.id
    if text == 'مشاهده سرویس‌های خرید شده':
        show_user_services(chat_id)
    elif text == 'خرید سرویس':
        start_service_purchase(chat_id)
    elif text == 'تعرفه‌ها':
        show_tariffs(chat_id)
    elif text == 'کیف پول و موجودی':
        show_wallet(chat_id)
    elif text == 'ارتقاء موجودی':
        show_wallet_charge_options(chat_id)
    elif text == 'تیکت و پشتیبانی':
        bot.send_message(chat_id, "لطفاً پیام یا سوال خود را برای ثبت تیکت ارسال کنید.")
        user_states[chat_id] = {'action': 'create_ticket'}
    elif text == 'راهنما':
        show_help(chat_id)
    elif text == 'قوانین':
        show_rules(chat_id)
    elif text == 'شارژ کیف پول':
        start_wallet_charge(chat_id)
    else:
        bot.send_message(chat_id, "لطفاً گزینه معتبر را انتخاب کنید.")

# توابع کمکی و مدیریت‌ها
def generate_sales_report():
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_services")
    total_orders = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(CASE WHEN service_name IS NOT NULL THEN 1 ELSE 0 END) FROM user_services")
    total_amount = cursor.fetchone()[0] or 0
    return f"گزارش کلی فروش:\nتعداد سفارش: {total_orders}\nمبلغ کل: {total_amount} تومان"

def manage_users(chat_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT user_id, username, wallet FROM users")
    users = cursor.fetchall()
    if not users:
        bot.send_message(chat_id, "در حال حاضر کاربری ثبت نشده است.")
        return
    txt = "لیست کاربران:\n"
    for u in users:
        user_id, username, wallet = u
        txt += f"ID: {user_id} | Username: @{username} | موجودی: {wallet} تومان\n"
    bot.send_message(chat_id, txt)

def show_user_services(chat_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT service_name, purchase_date FROM user_services WHERE user_id=?", (chat_id,))
    services = cursor.fetchall()
    if not services:
        bot.send_message(chat_id, "شما هیچ سرویسی خریداری نکرده‌اید.")
        return
    txt = "سرویس‌های خریداری شده:\n"
    for s in services:
        txt += f"- {s[0]} (تاریخ: {s[1]})\n"
    bot.send_message(chat_id, txt)

def start_service_purchase(chat_id):
    # نمونه، لیست سرویس‌ها رو می‌فرستی
    cursor = db.conn.cursor()
    cursor.execute("SELECT name, price FROM services")
    services = cursor.fetchall()
    if not services:
        bot.send_message(chat_id, "سرویس‌ها در حال حاضر موجود نیست.")
        return
    txt = "لیست سرویس‌ها:\n"
    for s in services:
        txt += f"{s[0]} - {s[1]} تومان\n"
    txt += "\nبرای خرید هر سرویس، نام آن را ارسال کنید."
    bot.send_message(chat_id, txt)

def show_tariffs(chat_id):
    bot.send_message(chat_id, "لیست تعرفه‌ها:\n1. سرویس A - 100 تومان\n2. سرویس B - 200 تومان")

def show_wallet(chat_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT wallet FROM users WHERE user_id=?", (chat_id,))
    res = cursor.fetchone()
    wallet_balance = res[0] if res else 0
    bot.send_message(chat_id, f"موجودی کیف پول شما: {wallet_balance} تومان")

def show_wallet_charge_options(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('شارژ با کارت به کارت', 'شارژ با درگاه')
    bot.send_message(chat_id, "روش شارژ را انتخاب کنید:", reply_markup=markup)
    user_states[chat_id] = {'action': 'charge_wallet_method'}

def handle_wallet_charge_method(chat_id, method):
    if method == 'شارژ با کارت به کارت':
        bot.send_message(chat_id, "لطفاً مبلغ مورد نظر را وارد کنید و شماره کارت خود را به همراه تصویر کارت ارسال کنید.")
        user_states[chat_id] = {'action': 'charge_card'}
    elif method == 'شارژ با درگاه':
        generate_payment_link(chat_id)
        user_states.pop(chat_id)
    else:
        bot.send_message(chat_id, "روش نامعتبر است. لطفاً مجدداً انتخاب کنید.")
        show_wallet_charge_options(chat_id)

def generate_payment_link(chat_id):
    link = "https://example.com/payment"  # لینک پرداخت واقعی رو جایگزین کن
    bot.send_message(chat_id, f"برای پرداخت، روی لینک زیر کلیک کنید:\n{link}")

def create_ticket(chat_id, question):
    cursor = db.conn.cursor()
    cursor.execute("INSERT INTO tickets (user_id, question, status) VALUES (?, ?, ?)", (chat_id, question, 'open'))
    db.conn.commit()
    bot.send_message(chat_id, "تیکت شما ثبت شد و تیم پشتیبانی در اسرع وقت تماس می‌گیرد.")

def show_help(chat_id):
    try:
        with open('templates/user_help.txt', 'r', encoding='utf-8') as f:
            bot.send_message(chat_id, f.read())
    except:
        bot.send_message(chat_id, "راهنما در دسترس نیست.")

def show_rules(chat_id):
    rules = db.get_setting('rules') or "قوانین در حال حاضر موجود نیست."
    bot.send_message(chat_id, rules)

def start_wallet_charge(chat_id):
    bot.send_message(chat_id, "لطفاً مبلغ مورد نظر برای شارژ را وارد کنید.")
    user_states[chat_id] = {'action': 'charge_amount'}

# مدیریت وضعیت‌های خاص
def handle_wallet_amount(chat_id, text):
    try:
        amount = int(text)
        if amount <= 0:
            raise ValueError
        update_user_wallet(chat_id, amount)
        bot.send_message(chat_id, f"مبلغ {amount} تومان به حساب شما اضافه شد.")
        user_states.pop(chat_id)
    except:
        bot.send_message(chat_id, "لطفاً مبلغ معتبر وارد کنید.")

def handle_card_image(chat_id, message):
    if message.content_type == 'photo':
        # در اینجا می‌تونی اطلاعات رو ثبت و تایید کنی
        # فرض بر این است که مبلغ رو قبلاً وارد کردی
        bot.send_message(chat_id, "تصویر کارت دریافت شد. پس از تایید، موجودی حساب شما شارژ می‌شود.")
        user_states.pop(chat_id)
    else:
        bot.send_message(chat_id, "لطفاً فقط تصویر را ارسال کنید.")

# مدیریت درخواست‌های افزایش موجودی
def handle_topup_requests(chat_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT id, user_id, amount, status FROM topup_requests WHERE status='pending'")
    requests = cursor.fetchall()
    if not requests:
        bot.send_message(chat_id, "درخواست‌های افزایش موجودی در حال حاضر وجود ندارد.")
        return
    for req in requests:
        req_id, user_id, amount, status = req
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("تایید", callback_data=f'topup_approve_{req_id}'),
            types.InlineKeyboardButton("رد", callback_data=f'topup_reject_{req_id}')
        )
        bot.send_message(user_id, f"درخواست افزایش موجودی به مبلغ {amount} تومان تایید یا رد شود.", reply_markup=markup)

# callback ها برای تایید و رد درخواست‌ها
@bot.callback_query_handler(func=lambda call: call.data.startswith('topup_'))
def handle_topup_callback(call):
    data = call.data.split('_')
    action = data[1]
    req_id = int(data[2])
    cursor = db.conn.cursor()
    cursor.execute("SELECT user_id, amount FROM topup_requests WHERE id=?", (req_id,))
    req = cursor.fetchone()
    if not req:
        bot.answer_callback_query(call.id, "درخواست یافت نشد.")
        return
    user_id, amount = req
    if action == 'approve':
        update_user_wallet(user_id, amount)
        cursor.execute("UPDATE topup_requests SET status='approved' WHERE id=?", (req_id,))
        db.conn.commit()
        bot.send_message(user_id, f"درخواست افزایش موجودی شما تایید شد. مبلغ {amount} تومان اضافه شد.")
        bot.answer_callback_query(call.id, "درخواست تایید شد.")
    elif action == 'reject':
        cursor.execute("UPDATE topup_requests SET status='rejected' WHERE id=?", (req_id,))
        db.conn.commit()
        bot.send_message(user_id, "درخواست افزایش موجودی شما رد شد.")
        bot.answer_callback_query(call.id, "درخواست رد شد.")

# تابع برای بروزرسانی موجودی کیف پول کاربر
def update_user_wallet(user_id, amount):
    cursor = db.conn.cursor()
    cursor.execute("UPDATE users SET wallet = wallet + ? WHERE user_id=?", (amount, user_id))
    db.conn.commit()

# ارسال پیام به همه کاربران
def send_broadcast(message_text):
    cursor = db.conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    for user in users:
        try:
            bot.send_message(user[0], message_text)
        except:
            pass

# تغییر وضعیت خرید سرویس
def toggle_service_status(chat_id):
    current = db.get_setting('service_active') or 'true'
    new_status = 'false' if current == 'true' else 'true'
    db.set_setting('service_active', new_status)
    bot.send_message(chat_id, f"وضعیت خرید سرویس به {new_status} تغییر یافت.")

# فایل اکسل آپلود شده
def handle_excel_upload(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        df = pd.read_excel(io.BytesIO(downloaded))
        for _, row in df.iterrows():
            apple_id = row.get('AppleID')
            owner_id = row.get('OwnerID')
            if apple_id and owner_id:
                cursor = db.conn.cursor()
                cursor.execute("INSERT INTO apple_ids (apple_id, owner_id) VALUES (?, ?)", (apple_id, owner_id))
        db.conn.commit()
        bot.send_message(message.chat.id, "اپل آی‌دی‌ها ثبت شد.")
        user_states.pop(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, "خطا در پردازش فایل. لطفاً مجدد سعی کنید.")
        print(e)

# اجرای ربات
bot.polling()