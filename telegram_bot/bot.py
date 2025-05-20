import telebot
from telebot import types
from config import TOKEN, ADMIN_IDS
import database as db

bot = telebot.TeleBot(TOKEN)

user_states = {}

# بررسی ادمین بودن
def is_admin(user_id):
    return user_id in ADMIN_IDS

# منوهای مرتب و زیبا
def user_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('مشاهده سرویس‌های خرید شده', 'خرید سرویس')
    markup.row('تعرفه‌ها', 'کیف پول و موجودی', 'ارتقاء موجودی')
    markup.row('تیکت و پشتیبانی', 'راهنما', 'قوانین')
    bot.send_message(message.chat.id, "به ربات خوش آمدید. لطفاً یکی از گزینه‌ها را انتخاب کنید.", reply_markup=markup)

def admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('گزارش‌های فروش', 'ارسال پیام به کاربران')
    markup.row('مدیریت کاربران', 'مدیریت درخواست‌های افزایش موجودی')
    markup.row('اپلیکیشن آی‌دی', 'وضعیت خرید سرویس')
    markup.row('مدیریت قوانین', 'راهنما')
    bot.send_message(message.chat.id, "پنل ادمین", reply_markup=markup)

# شروع
@bot.message_handler(commands=['start'])
def start_handler(message):
    if is_admin(message.from_user.id):
        admin_menu(message)
    else:
        user_menu(message)

# مدیریت دستورات عمومی
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.strip()
    if is_admin(message.from_user.id):
        handle_admin_commands(message, text)
    else:
        handle_user_commands(message, text)

# مدیریت ادمین
def handle_admin_commands(message, text):
    if text == 'گزارش‌های فروش':
        # نمونه گزارش واقعی
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE date >= DATE('now','start of day')")
        count_today = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(amount) FROM orders WHERE date >= DATE('now','start of day')")
        total_today = cursor.fetchone()[0] or 0
        report = f"فروش امروز:\nتعداد سفارش: {count_today}\nمبلغ کل: {total_today} تومان"
        bot.send_message(message.chat.id, report)
    elif text == 'ارسال پیام به کاربران':
        user_states[message.chat.id] = {'action': 'broadcast'}
        bot.send_message(message.chat.id, "پیام خود را برای ارسال به تمامی کاربران وارد کنید.")
    elif text == 'مدیریت کاربران':
        manage_users(message)
    elif text == 'مدیریت درخواست‌های افزایش موجودی':
        handle_topup_requests(message)
    elif text == 'اپلیکیشن آی‌دی':
        bot.send_message(message.chat.id, "لطفاً فایل اکسل حاوی اپل آیدی‌ها را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'upload_excel'}
    elif text == 'وضعیت خرید سرویس':
        status = db.get_setting('service_active') or 'true'
        new_status = 'false' if status == 'true' else 'true'
        db.set_setting('service_active', new_status)
        bot.send_message(message.chat.id, f"وضعیت خرید سرویس تغییر کرد به: {new_status}")
    elif text == 'مدیریت قوانین':
        bot.send_message(message.chat.id, "لطفاً متن قوانین جدید را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'edit_rules'}
    elif text == 'راهنما':
        with open('templates/admin_help.txt', 'r', encoding='utf-8') as f:
            bot.send_message(message.chat.id, f.read())
    elif text == 'گزارش‌های فروش':
        # نمونه گزارش
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(amount) FROM orders")
        total_amount = cursor.fetchone()[0] or 0
        report = f"گزارش کلی فروش:\nتعداد سفارش: {total_orders}\nمبلغ کل: {total_amount} تومان"
        bot.send_message(message.chat.id, report)
    elif text == 'مدیریت کاربران':
        manage_users(message)
    elif text == 'ارسال پیام به کاربران':
        user_states[message.chat.id] = {'action': 'broadcast'}
        bot.send_message(message.chat.id, "پیام خود را برای ارسال به تمامی کاربران وارد کنید.")
    elif text == 'مدیریت درخواست‌های افزایش موجودی':
        handle_topup_requests(message)
    elif text == 'اپلیکیشن آی‌دی':
        bot.send_message(message.chat.id, "لطفاً فایل اکسل حاوی اپل آیدی‌ها را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'upload_excel'}
    elif text == 'وضعیت خرید سرویس':
        status = db.get_setting('service_active') or 'true'
        new_status = 'false' if status == 'true' else 'true'
        db.set_setting('service_active', new_status)
        bot.send_message(message.chat.id, f"وضعیت خرید سرویس تغییر کرد به: {new_status}")
    elif text == 'مدیریت قوانین':
        bot.send_message(message.chat.id, "لطفاً متن قوانین جدید را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'edit_rules'}
    else:
        bot.send_message(message.chat.id, "دستور نامشخص است.")

# مدیریت درخواست‌های افزایش موجودی
def handle_topup_requests(message):
    cursor = db.conn.cursor()
    cursor.execute("SELECT id, user_id, amount, status FROM topup_requests WHERE status='pending'")
    requests = cursor.fetchall()
    if not requests:
        bot.send_message(message.chat.id, "درخواست‌های افزایش موجودی در حال حاضر وجود ندارد.")
        return
    for req in requests:
        req_id, user_id, amount, status = req
        user = bot.get_chat(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("تایید", callback_data=f'topup_approve_{req_id}'),
            types.InlineKeyboardButton("رد", callback_data=f'topup_reject_{req_id}')
        )
        bot.send_message(user_id, f"درخواست افزایش موجودی به مبلغ {amount} تومان تایید یا رد شود.", reply_markup=markup)

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
        # بروزرسانی موجودی کاربر
        cursor.execute("UPDATE users SET wallet = wallet + ? WHERE user_id=?", (amount, user_id))
        cursor.execute("UPDATE topup_requests SET status='approved' WHERE id=?", (req_id,))
        db.conn.commit()
        bot.send_message(user_id, f"درخواست افزایش موجودی شما تایید شد. مبلغ {amount} تومان اضافه شد.")
        bot.answer_callback_query(call.id, "درخواست تایید شد.")
    elif action == 'reject':
        cursor.execute("UPDATE topup_requests SET status='rejected' WHERE id=?", (req_id,))
        db.conn.commit()
        bot.send_message(user_id, "درخواست افزایش موجودی شما رد شد.")
        bot.answer_callback_query(call.id, "درخواست رد شد.")

# مدیریت کاربران (لیست و حذف)
def manage_users(message):
    cursor = db.conn.cursor()
    cursor.execute("SELECT user_id, username, wallet FROM users")
    users = cursor.fetchall()
    if not users:
        bot.send_message(message.chat.id, "در حال حاضر کاربری ثبت نشده است.")
        return
    txt = "لیست کاربران:\n"
    for u in users:
        user_id, username, wallet = u
        txt += f"ID: {user_id} | Username: @{username} | موجودی: {wallet} تومان\n"
    bot.send_message(message.chat.id, txt)

# پیام به تمام کاربران
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    if user_states.get(message.chat.id, {}).get('action') == 'broadcast':
        # ارسال پیام به همه
        cursor = db.conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        for user_id in users:
            try:
                bot.send_message(user_id[0], message.text)
            except:
                pass
        bot.send_message(message.chat.id, "پیام به تمامی کاربران ارسال شد.")
        user_states.pop(message.chat.id)
    elif user_states.get(message.chat.id, {}).get('action') == 'upload_excel':
        # فایل اکسل
        pass
    elif user_states.get(message.chat.id, {}).get('action') == 'edit_rules':
        # ویرایش قوانین
        db.set_setting('rules', message.text)
        bot.send_message(message.chat.id, "قوانین بروزرسانی شد.")
        user_states.pop(message.chat.id)
    elif user_states.get(message.chat.id, {}).get('action') == 'create_ticket':
        # ثبت تیکت
        cursor = db.conn.cursor()
        cursor.execute("INSERT INTO tickets (user_id, question, status) VALUES (?, ?, ?)", (message.from_user.id, message.text, 'open'))
        db.conn.commit()
        bot.send_message(message.chat.id, "تیکت شما ثبت شد و تیم پشتیبانی در اسرع وقت تماس می‌گیرد.")
        user_states.pop(message.chat.id)
    # ... موارد دیگر
    else:
        pass

# ارسال فایل اکسل
@bot.message_handler(content_types=['document'])
def handle_documents(message):
    if user_states.get(message.chat.id, {}).get('action') == 'upload_excel':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        df = pd.read_excel(io.BytesIO(downloaded_file))
        for index, row in df.iterrows():
            apple_id = row.get('AppleID')
            owner_id = row.get('OwnerID')
            if apple_id and owner_id:
                try:
                    db.cursor.execute("INSERT INTO apple_ids (apple_id, owner_id) VALUES (?, ?)", (apple_id, owner_id))
                except:
                    pass
        db.conn.commit()
        bot.send_message(message.chat.id, "اپل آی‌دی‌ها ثبت شد.")
        user_states.pop(message.chat.id)
    else:
        bot.send_message(message.chat.id, "در انتظار فایل اکسل نبودم.")

# اجرای ربات
bot.polling()