import asyncio
import os
import sqlite3
import openpyxl
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command
from config import TOKEN, ADMIN_IDS
from app.utils import database as db

# --- راه‌اندازی بات ---
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- کیبوردهای کاربر ---
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛒 خرید سرویس"), KeyboardButton(text="💼 کیف پول"))
    kb.row(KeyboardButton(text="📄 سوابق خرید"), KeyboardButton(text="📖 راهنما"))
    return kb.as_markup(resize_keyboard=True)

# --- کیبوردهای ادمین ---
def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛠️ مدیریت کاربران"), KeyboardButton(text="📢 ارسال پیام به همه"))
    kb.row(KeyboardButton(text="➕ افزودن اپل آیدی متنی"), KeyboardButton(text="🚀 آپلود فایل اکسل"))
    kb.row(KeyboardButton(text="🔧 تغییر وضعیت فروش"), KeyboardButton(text="🔙 بازگشت"))
    return kb.as_markup(resize_keyboard=True)

# --- استیت‌ها ---
class AdminStates(StatesGroup):
    adding_apple_ids_text = State()
    uploading_excel = State()
    broadcasting = State()

# --- بررسی ادمین ---
def is_admin(user_id):
    return user_id in ADMIN_IDS

# --- شروع ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    db.add_user(user_id, message.from_user.username)
    await message.answer("🌟 به ربات فروش اپل آی‌دی خوش آمدید!", reply_markup=main_menu())
    if is_admin(user_id):
        await message.answer("👑 وارد پنل ادمین شدید.", reply_markup=admin_menu())

# --- خرید سرویس ---
@dp.message(F.text == "🛒 خرید سرویس")
async def buy_service(m: types.Message):
    if not db.get_service_status():
        await m.answer("🚫 فروش در حال حاضر بسته است.")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text='💳 کارت به کارت'), KeyboardButton(text='💼 کیف پول')]
    ])
    await m.answer("روش پرداخت مورد نظر خود را انتخاب کنید:", reply_markup=markup)

# --- کیف پول ---
@dp.message(F.text == "💼 کیف پول")
async def wallet(m: types.Message):
    user = db.get_user(m.from_user.id)
    balance = user[2] if user else 0
    await m.answer(f"💰 موجودی کیف پول شما: {balance} تومان", reply_markup=main_menu())

# --- سوابق خرید ---
@dp.message(F.text == "📄 سوابق خرید")
async def orders_history(m: types.Message):
    orders = db.get_user_orders(m.from_user.id)
    if not orders:
        await m.answer("📭 هیچ خریدی ثبت نشده است.")
        return
    msg = "📝 سوابق خریدهای شما:\n"
    for order in orders:
        msg += f"• اپل آیدی: {order[2]} | مبلغ: {order[3]} | وضعیت: {order[4]}\n"
    await m.answer(msg)

# --- راهنما ---
@dp.message(F.text == "📖 راهنما")
async def guide(m: types.Message):
    text = """
🎉 به ربات فروش اپل آیدی خوش آمدید!

🔹 برای خرید، گزینه "🛒 خرید سرویس" را انتخاب کنید.
🔹 برای شارژ کیف پول، قسمت "💼 کیف پول" را استفاده کنید.
🔹 سوابق خرید در قسمت مربوطه نمایش داده می‌شود.
🌟 در صورت نیاز به پشتیبانی، با ادمین تماس بگیرید.
"""
    await m.answer(text)

# --- روش خرید ---
@dp.message(F.text.in_(["💳 کارت به کارت", "💼 کیف پول"]))
async def purchase_method(m: types.Message):
    if m.text == "💳 کارت به کارت":
        await m.answer("لطفاً رسید پرداخت خود را ارسال کنید تا بررسی شود.")
    else:
        user = db.get_user(m.from_user.id)
        await m.answer(f"موجودی کیف پول شما: {user[2]} تومان")

# --- رسید پرداخت ---
@dp.message(F.content_type.in_(['photo', 'document']))
async def receive_receipt(m: types.Message):
    await m.answer("رسید شما دریافت شد و در حال بررسی است.")

# --- مدیریت کاربران ---
@dp.message(F.text == "🛠️ مدیریت کاربران")
async def manage_users(m: types.Message):
    if not is_admin(m.from_user.id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, blocked FROM users")
    users = c.fetchall()
    conn.close()
    for u in users:
        status = "🟢 فعال" if u[2]==0 else "🔴 مسدود"
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"{u[1]} ({u[0]}) - {status}", callback_data=f"user_{u[0]}")
        ])
    await m.answer("لیست کاربران:", reply_markup=kb)

@dp.callback_query(F.data.startswith("user_"))
async def manage_user_callback(c: types.CallbackQuery):
    user_id = int(c.data.split('_')[1])
    user = db.get_user(user_id)
    if user:
        new_blocked = 0 if user[3]==1 else 1
        db.set_user_blocked(user_id, bool(new_blocked))
        status_text = "فعال" if new_blocked == 0 else "مسدود"
        await c.answer(f"کاربر {user_id} به حالت {status_text} تغییر کرد.")
        await manage_users(c.message)

# --- پیام همگانی ---
@dp.message(F.text == "📢 ارسال پیام به همه")
async def broadcast_message(m: types.Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        return
    await m.answer("متن پیام را ارسال کنید:")
    await state.set_state(AdminStates.broadcasting)

@dp.message(AdminStates.broadcasting)
async def process_broadcast(m: types.Message, state: FSMContext):
    text = m.text
    users = db.get_all_users()
    for uid in users:
        try:
            await bot.send_message(uid, text)
        except:
            continue
    await m.answer("پیام به همه کاربران ارسال شد.", reply_markup=admin_menu())
    await state.clear()

# --- افزودن اپل آیدی متنی ---
@dp.message(F.text == "➕ افزودن اپل آیدی متنی")
async def add_apple_ids_text(m: types.Message, state: FSMContext):
    await m.answer("اپل آیدی‌ها را هرکدام در یک خط وارد کنید:")
    await state.set_state(AdminStates.adding_apple_ids_text)

@dp.message(AdminStates.adding_apple_ids_text)
async def save_apple_ids_text(m: types.Message, state: FSMContext):
    ids = m.text.splitlines()
    for aid in ids:
        aid = aid.strip()
        if aid:
            db.add_apple_id(aid)
    await m.answer("✅ اپل آیدی‌ها ثبت شدند.", reply_markup=admin_menu())
    await state.clear()

# --- آپلود اکسل ---
@dp.message(F.document)
async def upload_excel(m: types.Message):
    if not is_admin(m.from_user.id):
        return
    file = m.document
    path = f"uploads/{file.file_name}"
    os.makedirs('uploads', exist_ok=True)
    await bot.download(file, destination=path)
    wb = openpyxl.load_workbook(path)
    sheet = wb.active
    ids = []
    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if cell:
                ids.append(str(cell))
    db.add_apple_ids_from_excel(ids)
    await m.answer("📥 اپل آیدی‌ها از فایل اکسل اضافه شدند.", reply_markup=admin_menu())

# --- تغییر وضعیت فروش ---
@dp.message(F.text == "🔧 تغییر وضعیت فروش")
async def change_status(m: types.Message):
    if not is_admin(m.from_user.id):
        return
    db.toggle_service_status()
    status = "باز" if db.get_service_status() else "بسته"
    await m.answer(f"وضعیت فروش اکنون: {status}", reply_markup=admin_menu())

# --- پیام پیش‌فرض ---
@dp.message()
async def default_response(m: types.Message):
    await m.answer("لطفاً از منوی زیر استفاده کنید.", reply_markup=main_menu())

# --- اجرای بات ---
async def main():
    db.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
