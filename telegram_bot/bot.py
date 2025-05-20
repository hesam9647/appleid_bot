import telebot
from telebot import types
from config import TOKEN, ADMIN_IDS, CHANNEL_ID
import database as db
import utils
import io
import pandas as pd

bot = telebot.TeleBot(TOKEN)

# حالت‌های کاربری
user_states = {}

# چک کردن کاربر ادمین یا مشتری
def check_user(user_id):
    return 'admin' if utils.is_admin(user_id) else 'user'

# پیام خوش‌آمدگویی و منوهای اولیه
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_type = check_user(message.from_user.id)
    if user_type == 'admin':
        admin_panel(message)
    else:
        user_menu(message)

def user_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('مشاهده سرویس‌های خرید شده', 'خرید سرویس', 'راهنما', 'تیکت و پشتیبانی', 'تعرفه‌ها', 'کیف پول و موجودی', 'قوانین')
    bot.send_message(message.chat.id, "به ربات خوش آمدید. لطفاً یکی از گزینه‌ها را انتخاب کنید.", reply_markup=markup)

def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('گزارش‌های فروش', 'ارسال پیام به کاربران')
    markup.row('مدیریت کاربران', 'اپلیکیشن آی‌دی', 'وضعیت خرید سرویس')
    markup.row('مدیریت قوانین', 'راهنما')
    bot.send_message(message.chat.id, "پنل ادمین", reply_markup=markup)

# مدیریت دستورات عمومی
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text
    user_type = check_user(message.from_user.id)

    if user_type == 'admin':
        handle_admin_commands(message, text)
    else:
        handle_user_commands(message, text)

# دستورات ادمین
def handle_admin_commands(message, text):
    if text == 'گزارش‌های فروش':
        # نمونه گزارش
        bot.send_message(message.chat.id, "گزارش فروش امروز:\n- تعداد ثبت‌نام: ۱۰\n- مبلغ فروش: ۵۰۰ هزار تومان")
    elif text == 'ارسال پیام به کاربران':
        user_states[message.chat.id] = {'action': 'broadcast'}
        bot.send_message(message.chat.id, "پیام مورد نظر خود را ارسال کنید تا به تمام کاربران ارسال شود.")
    elif text == 'مدیریت کاربران':
        manage_users(message)
    elif text == 'اپلیکیشن آی‌دی':
        bot.send_message(message.chat.id, "لطفاً فایل اکسل حاوی اپل آیدی‌ها را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'upload_excel'}
    elif text == 'وضعیت خرید سرویس':
        current_status = db.get_setting('service_active') or 'true'
        new_status = 'false' if current_status == 'true' else 'true'
        db.set_setting('service_active', new_status)
        bot.send_message(message.chat.id, f"وضعیت خرید سرویس تغییر کرد به: {new_status}")
    elif text == 'مدیریت قوانین':
        bot.send_message(message.chat.id, "لطفاً متن قوانین جدید را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'edit_rules'}
    elif text == 'راهنما':
        with open('templates/admin_help.txt', 'r', encoding='utf-8') as f:
            bot.send_message(message.chat.id, f.read())
    elif text == 'تعرفه‌ها':
        bot.send_message(message.chat.id, "تعرفه‌ها در حال حاضر در دسترس نیست.")
    elif text == 'خرید سرویس':
        # نمونه سرویس‌ها
        services = [('سرویس ۱', 100), ('سرویس ۲', 200)]
        markup = types.InlineKeyboardMarkup()
        for name, price in services:
            btn = types.InlineKeyboardButton(f"{name} - {price} تومان", callback_data=f'buy_{name}')
            markup.add(btn)
        bot.send_message(message.chat.id, "انتخاب سرویس:", reply_markup=markup)
    elif text == 'خلاصه وضعیت':
        # وضعیت خرید سرویس
        status = db.get_setting('service_active') or 'true'
        bot.send_message(message.chat.id, f"وضعیت فعال بودن خرید سرویس: {status}")
    elif text == 'مدیریت قوانین':
        bot.send_message(message.chat.id, "لطفاً متن قوانین جدید را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'edit_rules'}
    else:
        bot.send_message(message.chat.id, "دستور نامشخص است.")

# مدیریت دستورات کاربران
def handle_user_commands(message, text):
    if text == 'راهنما':
        with open('templates/user_help.txt', 'r', encoding='utf-8') as f:
            bot.send_message(message.chat.id, f.read())
    elif text == 'مشاهده سرویس‌های خرید شده':
        # نمونه نمایش خریدها
        bot.send_message(message.chat.id, "شما خریدهای زیر را دارید:\n- سرویس ۱\n- سرویس ۲")
    elif text == 'خرید سرویس':
        services = [('سرویس ۱', 100), ('سرویس ۲', 200)]
        markup = types.InlineKeyboardMarkup()
        for name, price in services:
            btn = types.InlineKeyboardButton(f"{name} - {price} تومان", callback_data=f'buy_{name}')
            markup.add(btn)
        bot.send_message(message.chat.id, "انتخاب سرویس:", reply_markup=markup)
    elif text == 'تیکت و پشتیبانی':
        bot.send_message(message.chat.id, "برای ارسال تیکت، لطفاً سوال خود را بنویسید.")
        user_states[message.chat.id] = {'action': 'create_ticket'}
    elif text == 'تعرفه‌ها':
        bot.send_message(message.chat.id, "تعرفه‌ها در حال حاضر در دسترس نیست.")
    elif text == 'کیف پول و موجودی':
        cursor = db.cursor
        cursor.execute("SELECT wallet FROM users WHERE user_id=?", (message.from_user.id,))
        result = cursor.fetchone()
        balance = result[0] if result else 0
        bot.send_message(message.chat.id, f"موجودی کیف پول شما: {balance} تومان")
    elif text == 'قوانین':
        bot.send_message(message.chat.id, "متن قوانین در حال حاضر در دسترس نیست.")
    elif text == 'خرید اپل آی‌دی':
        bot.send_message(message.chat.id, "لطفاً فایل اکسل حاوی اپل آیدی‌ها را ارسال کنید.")
        user_states[message.chat.id] = {'action': 'upload_excel'}
    else:
        bot.send_message(message.chat.id, "دستور نامشخص است.")

# مدیریت فایل‌های اکسل اپل آیدی‌ها
@bot.message_handler(content_types=['document'])
def handle_documents(message):
    if user_states.get(message.chat.id, {}).get('action') == 'upload_excel':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        df = pd.read_excel(io.BytesIO(downloaded_file))
        # فرض بر این است که ستون‌ها شامل 'AppleID' و 'OwnerID' هستند
        for index, row in df.iterrows():
            apple_id = row['AppleID']
            owner_id = row['OwnerID']
            try:
                db.cursor.execute("INSERT INTO apple_ids (apple_id, owner_id) VALUES (?, ?)", (apple_id, owner_id))
            except:
                pass
        db.conn.commit()
        bot.send_message(message.chat.id, "اپل آی‌دی‌ها ثبت شد و فایل پاک شد.")
        user_states.pop(message.chat.id)
    else:
        bot.send_message(message.chat.id, "فایلی در انتظار آپلود نیست.")

# پیام‌های متنی
@bot.message_handler(func=lambda m: True)
def handle_texts(message):
    state = user_states.get(message.chat.id)
    if state:
        action = state.get('action')
        if action == 'create_ticket':
            # ثبت تیکت
            cursor = db.cursor
            cursor.execute("INSERT INTO tickets (user_id, question, status) VALUES (?, ?, ?)", (message.from_user.id, message.text, 'open'))
            db.conn.commit()
            bot.send_message(message.chat.id, "تیکت شما ثبت شد و تیم پشتیبانی در اسرع وقت تماس می‌گیرد.")
            user_states.pop(message.chat.id)
        elif action == 'edit_rules':
            # بروزرسانی قوانین
            db.set_setting('rules', message.text)
            bot.send_message(message.chat.id, "قوانین بروزرسانی شد.")
            user_states.pop(message.chat.id)
        elif action == 'broadcast':
            # ارسال پیام به همه کاربران
            cursor = db.cursor
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()
            for user in users:
                try:
                    bot.send_message(user[0], message.text)
                except:
                    pass
            bot.send_message(message.chat.id, "پیام شما به تمام کاربران ارسال شد.")
            user_states.pop(message.chat.id)
        elif action == 'upload_apple_ids':
            # اگر نیاز به عملیات خاص دارید در اینجا انجام دهید
            pass
    else:
        # در صورت نیاز، عملیات دیگر
        pass

# callback handler برای خرید سرویس
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
    service_name = call.data.replace('buy_', '')
    # فرض بر این است که عملیات پرداخت و ثبت سفارش انجام می‌شود
    # در این نمونه، فقط پیام تأیید
    bot.answer_callback_query(call.id, f"خرید {service_name} انجام شد.")
    bot.send_message(call.message.chat.id, f"سرویس {service_name} با موفقیت خریداری شد.")

# قسمت افزودن اپل آیدی و ارسال نکات پس از خرید
def send_apple_id_info(chat_id, apple_id, password, support_id, formation_date, email, email_password):
    # متن اپل آیدی
    apple_info = f"""
Apple ID: {apple_id}
Password: {password}
Support ID: {support_id}
Date of formation: {formation_date}
Email: {email}
Email Password: {email_password}
"""
    tips = """
☑️ حتما گزینه Find My iPhone را خاموش کنید!
در صورت فعال بودن این گزینه، فرآیند فعال‌سازی آی‌کلود دچار مشکل می‌شود و مسئولیت آن بر عهده خودتان است.

☑️ Location Service (موقعیت‌یابی) را خاموش کنید.

☑️ از VPN با آی‌پی ثابت استفاده کنید.  
پیشنهاد ما OpenVPN و SSH است.  
از V2ray به دلیل نشت زیاد، پرهیز کنید.

☑️ فقط یک اپل آی‌دی را روی یک دستگاه فعال کنید.

❗️ فقط از اپ استور اپل آی‌دی استفاده کنید و وارد برنامه‌های دیگر نکنید.

🔑 پسورد اپل آی‌دی را پس از تحویل حتماً تغییر دهید.

⚠️ توجه: اگر Find My iPhone فعال باشد و آی‌کلود قفل شود، مجموعه ما مسئولیتی در قبال قفل شدن ندارد. لطفاً این نکات را رعایت کنید تا مشکلی پیش نیاید.
"""
    bot.send_message(chat_id, "اطلاعات اپل آی‌دی:\n" + apple_info)
    bot.send_message(chat_id, tips)

# نمونه درخواست برای ارسال آی‌دی پس از خرید
def process_new_apple_id(chat_id, apple_id, password, support_id, formation_date, email, email_password):
    # ثبت در دیتابیس
    try:
        db.cursor.execute("INSERT INTO apple_ids (apple_id, password, support_id, formation_date, email, email_password) VALUES (?, ?, ?, ?, ?, ?)",
                          (apple_id, password, support_id, formation_date, email, email_password))
        db.conn.commit()
        # ارسال به کاربر
        send_apple_id_info(chat_id, apple_id, password, support_id, formation_date, email, email_password)
    except Exception as e:
        bot.send_message(chat_id, "خطا در ثبت اطلاعات: " + str(e))

# راه‌اندازی ربات
if __name__ == '__main__':
    bot.polling()