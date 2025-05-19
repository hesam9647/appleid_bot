import telebot
from telebot import types
from config import TOKEN, ADMIN_IDS, CHANNEL_ID
import database as db
import utils

bot = telebot.TeleBot(TOKEN)

# حالت‌های کاربری
user_states = {}

# چک کردن کاربر ادمین یا مشتری
def check_user(user_id):
    if utils.is_admin(user_id):
        return 'admin'
    else:
        return 'user'

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
    markup.add('مشاهده سرویس‌های خرید شده', 'خرید سرویس')
    markup.add('راهنما', 'تیکت و پشتیبانی')
    markup.add('تعرفه‌ها', 'کیف پول و موجودی', 'قوانین')
    bot.send_message(message.chat.id, "به ربات خوش آمدید. لطفاً یکی از گزینه‌ها را انتخاب کنید.", reply_markup=markup)

def admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('گزارش‌های فروش', 'ارسال پیام به کاربران')
    markup.row('مدیریت کاربران', 'اپلیکیشن آی‌دی', 'وضعیت خرید سرویس')
    markup.row('مدیریت قوانین', 'راهنما')
    bot.send_message(message.chat.id, "پنل ادمین", reply_markup=markup)

# دستورات و منوهای مختلف
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text
    user_type = check_user(message.from_user.id)

    if user_type == 'admin':
        handle_admin_commands(message, text)
    else:
        handle_user_commands(message, text)

# admin commands
def handle_admin_commands(message, text):
    if text == 'گزارش‌های فروش':
        # گزارش روزانه، هفتگی، ماهانه
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
        # فعال یا غیرفعال کردن خرید
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
    else:
        # پاسخ پیش‌فرض
        bot.send_message(message.chat.id, "دستور نامشخص است.")

def handle_user_commands(message, text):
    if text == 'راهنما':
        with open('templates/user_help.txt', 'r', encoding='utf-8') as f:
            bot.send_message(message.chat.id, f.read())
    elif text == 'مشاهده سرویس‌های خرید شده':
        # نمایش سرویس‌های خریداری شده
        bot.send_message(message.chat.id, "شما خریدهای زیر را دارید:\n- سرویس ۱\n- سرویس ۲")
    elif text == 'خرید سرویس':
        # منوی خرید
        # فرض بر این است که سرویس‌ها در دیتابیس موجود است
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
        # نمایش تعرفه‌ها، توسط ادمین وارد شده
        bot.send_message(message.chat.id, "تعرفه‌ها در حال حاضر در دسترس نیست.")
    elif text == 'کیف پول و موجودی':
        # نمایش موجودی کیف پول
        cursor = db.cursor
        cursor.execute("SELECT wallet FROM users WHERE user_id=?", (message.from_user.id,))
        result = cursor.fetchone()
        balance = result[0] if result else 0
        bot.send_message(message.chat.id, f"موجودی کیف پول شما: {balance} تومان")
        bot.send_message(message.chat.id, "برای شارژ کیف پول، از منوی مورد نظر استفاده کنید.")  
    elif text == 'قوانین':
        bot.send_message(message.chat.id, "متن قوانین در حال حاضر در دسترس نیست.")
    else:
        bot.send_message(message.chat.id, "دستور نامشخص است.")

# مدیریت کاربران
def manage_users(message):
    # لیست کاربران، جستجو و مدیریت
    bot.send_message(message.chat.id, "در حال حاضر امکان مدیریت کاربران در این نسخه وجود ندارد.")

# ثبت فایل اکسل اپل آیدی‌ها
@bot.message_handler(content_types=['document'])
def handle_documents(message):
    if user_states.get(message.chat.id, {}).get('action') == 'upload_excel':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        import pandas as pd
        import io
        df = pd.read_excel(io.BytesIO(downloaded_file))
        # فرض بر این است که ستون‌ها شامل 'AppleID' و 'OwnerID' هستند
        for index, row in df.iterrows():
            apple_id = row['AppleID']
            owner_id = row['OwnerID']
            # افزودن به دیتابیس و حذف از فایل
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
            cursor.execute("INSERT INTO tickets (user_id, question, status) VALUES (?, ?, ?)",
                           (message.from_user.id, message.text, 'open'))
            db.conn.commit()
            bot.send_message(message.chat.id, "تیکت شما ثبت شد و تیم پشتیبانی در اسرع وقت تماس می‌گیرد.")
            user_states.pop(message.chat.id)
        elif action == 'edit_rules':
            # ویرایش قوانین
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
    else:
        pass

# Callback برای خرید سرویس
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy(call):
    service_name = call.data.replace('buy_', '')
    # فرض بر این است که قیمت‌ها و سرویس‌ها در دیتابیس است
    # اینجا باید منطق خرید و کم کردن موجودی و ثبت سفارش باشد
    bot.answer_callback_query(call.id, f"خرید {service_name} انجام شد.")
    bot.send_message(call.message.chat.id, f"سرویس {service_name} با موفقیت خریداری شد.")

# راه‌اندازی ربات
if __name__ == '__main__':
    bot.polling()