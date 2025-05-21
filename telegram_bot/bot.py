import telebot
from telebot import types
from config import TOKEN, ADMIN_IDS
import database as db
import re

bot = telebot.TeleBot(TOKEN)

user_states = {}

# بررسی ادمین بودن
def is_admin(user_id):
    return user_id in ADMIN_IDS

# منوهای مرتب و زیبا (کاربر)
def user_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        types.KeyboardButton('مشاهده سرویس‌های خریداری شده'),
        types.KeyboardButton('خرید سرویس'),
        types.KeyboardButton('تعرفه‌ها'),
        types.KeyboardButton('کیف پول و موجودی'),
        types.KeyboardButton('ارتقاء موجودی'),
        types.KeyboardButton('تیکت و پشتیبانی'),
        types.KeyboardButton('راهنما'),
        types.KeyboardButton('قوانین')
    )
    bot.send_message(message.chat.id, "لطفا یکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)


# منوهای مرتب و زیبا (ادمین)
def admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        types.KeyboardButton('افزودن اپل آیدی'),
        types.KeyboardButton('مدیریت کاربران'),
        types.KeyboardButton('مشاهده تیکت‌ها'),
        types.KeyboardButton('راهنما'),
        types.KeyboardButton('بازگشت به منو اصلی')  # مهم!
    )
    bot.send_message(message.chat.id, "منوی ادمین:", reply_markup=markup)



# ... (بقیه توابع)

# مثال برای خرید سرویس (توجه به ساختار)
def buy_service(message):
    # ... (کد برای نمایش لیست سرویس‌ها و گرفتن انتخاب کاربر)
    markup = types.InlineKeyboardMarkup()
    # ... (ساخت دکمه‌های پرداخت با لینک یا اطلاعات پرداخت)
    bot.send_message(message.chat.id, "لطفا اطلاعات پرداخت را تکمیل کنید.", reply_markup=markup)


# ... (بقیه توابع)

# مثال برای کیف پول و موجودی
def show_balance(message):
   # ... (کد برای دریافت موجودی از دیتابیس)
   balance = db.get_user_balance(message.from_user.id)
   if balance is not None:
       bot.send_message(message.chat.id, f"موجودی شما: {balance} تومان")
   else:
       bot.send_message(message.chat.id, "متاسفم، اطلاعات موجودی شما در دسترس نیست.")

# ... (بقیه توابع)


# ... (بقیه کدها)

@bot.message_handler(commands=['start'])
def start(message):
    user_menu(message)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'مشاهده سرویس‌های خریداری شده':
        # ... (کد برای نمایش لیست سرویس‌های خریداری شده کاربر)
        pass
    elif message.text == 'خرید سرویس':
        buy_service(message)
    elif message.text == 'کیف پول و موجودی':
        show_balance(message)
    elif message.text == 'ارتقاء موجودی':
        # ... (کد برای ارتقاء موجودی)
        pass
    elif message.text == 'تیکت و پشتیبانی':
        # ... (کد برای ایجاد تیکت)
        pass
    # ... (بقیه دستورات)
    # ... (بررسی ادمین بودن و دستورات ادمین)
    elif is_admin(message.from_user.id):
        if message.text == 'افزودن اپل آیدی':
            # ... (کد برای گرفتن اپل آیدی از ادمین)
            pass
        elif message.text == 'مدیریت کاربران':
            # ... (کد برای مدیریت کاربران)
            pass
        elif message.text == 'مشاهده تیکت‌ها':
            # ... (کد برای نمایش تیکت‌ها)
            pass
        elif message.text == 'راهنما':
            # ... (کد برای نمایش راهنمای ادمین)
            pass
        elif message.text == 'بازگشت به منو اصلی':
            admin_menu(message)  # بازگشت به منو ادمین
    # اگر دستوری ناشناخته بود:
    else:
        bot.send_message(message.chat.id, "دستور نامشخص است.")



bot.polling(none_stop=True)
