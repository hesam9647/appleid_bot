import asyncio
import os
import sqlite3
import openpyxl
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputFile
)
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
    kb.row(KeyboardButton(text="📄 سوابق خرید"), KeyboardButton(text="🎫 تیکت پشتیبانی"))
    kb.row(KeyboardButton(text="📖 راهنما"))
    return kb.as_markup(resize_keyboard=True)

# --- کیبوردهای ادمین ---
def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛠️ مدیریت کاربران"), KeyboardButton(text="📢 ارسال پیام به همه"))
    kb.row(KeyboardButton(text="➕ افزودن اپل آیدی متنی"), KeyboardButton(text="🚀 آپلود فایل اکسل"))
    kb.row(KeyboardButton(text="🎫 تیکت‌های پشتیبانی"), KeyboardButton(text="🔧 تغییر وضعیت فروش"))
    return kb.as_markup(resize_keyboard=True)

# --- استیت‌ها ---
class AdminStates(StatesGroup):
    adding_apple_ids_text = State()
    broadcasting = State()
    replying_ticket = State()

class TicketStates(StatesGroup):
    waiting_title = State()
    waiting_question = State()

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
🌟 در صورت نیاز به پشتیبانی، از بخش "🎫 تیکت پشتیبانی" استفاده کنید.
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

# --- دریافت رسید پرداخت ---
@dp.message(F.content_type.in_(["photo", "document"]))
async def receive_receipt(m: types.Message):
    await m.answer("رسید شما دریافت شد و در حال بررسی است.")

# --- مدیریت کاربران ---
@dp.message(F.text == "🛠️ مدیریت کاربران")
async def manage_users(m: types.Message):
    if not is_admin(m.from_user.id): return
    users = db.get_all_users(full=True)
    for u in users:
        status = "🟢 فعال" if not u[2] else "🔴 مسدود"
        text = f"👤 {u[1]} ({u[0]}) - {status}"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 تغییر وضعیت", callback_data=f"toggle_{u[0]}")]
        ])
        await m.answer(text, reply_markup=buttons)

@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_user(c: types.CallbackQuery):
    user_id = int(c.data.split('_')[1])
    db.toggle_user_blocked(user_id)
    await c.answer("✅ وضعیت کاربر تغییر کرد.")
    await c.message.delete()

# --- ارسال پیام همگانی ---
@dp.message(F.text == "📢 ارسال پیام به همه")
async def broadcast_message(m: types.Message, state: FSMContext):
    if not is_admin(m.from_user.id): return
    await m.answer("متن پیام را ارسال کنید:")
    await state.set_state(AdminStates.broadcasting)

@dp.message(AdminStates.broadcasting)
async def process_broadcast(m: types.Message, state: FSMContext):
    for uid in db.get_all_user_ids():
        try:
            await bot.send_message(uid, m.text)
        except:
            pass
    await m.answer("📢 پیام ارسال شد.", reply_markup=admin_menu())
    await state.clear()

# --- افزودن اپل آیدی متنی ---
@dp.message(F.text == "➕ افزودن اپل آیدی متنی")
async def add_apple_ids_text(m: types.Message, state: FSMContext):
    await m.answer("اپل آیدی‌ها را هرکدام در یک خط وارد کنید:")
    await state.set_state(AdminStates.adding_apple_ids_text)

@dp.message(AdminStates.adding_apple_ids_text)
async def save_apple_ids_text(m: types.Message, state: FSMContext):
    for line in m.text.splitlines():
        if line.strip():
            db.add_apple_id(line.strip())
    await m.answer("✅ اپل آیدی‌ها ذخیره شدند.", reply_markup=admin_menu())
    await state.clear()

# --- آپلود اکسل ---
@dp.message(F.document)
async def upload_excel(m: types.Message):
    if not is_admin(m.from_user.id): return
    file = m.document
    path = f"uploads/{file.file_name}"
    os.makedirs("uploads", exist_ok=True)
    await bot.download(file, destination=path)
    wb = openpyxl.load_workbook(path)
    for row in wb.active.iter_rows(values_only=True):
        for cell in row:
            if cell:
                db.add_apple_id(str(cell))
    await m.answer("✅ اپل آیدی‌ها از فایل اکسل افزوده شدند.", reply_markup=admin_menu())

# --- تغییر وضعیت فروش ---
@dp.message(F.text == "🔧 تغییر وضعیت فروش")
async def toggle_status(m: types.Message):
    if not is_admin(m.from_user.id): return
    db.toggle_service_status()
    status = "باز" if db.get_service_status() else "بسته"
    await m.answer(f"وضعیت فروش: {status}", reply_markup=admin_menu())

# --- تیکت پشتیبانی ---
@dp.message(F.text == "🎫 تیکت پشتیبانی")
async def start_ticket(m: types.Message, state: FSMContext):
    await m.answer("🔸 لطفا عنوان تیکت را وارد کنید:")
    await state.set_state(TicketStates.waiting_title)

@dp.message(TicketStates.waiting_title)
async def ticket_title(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text)
    await m.answer("✏️ حالا سوال خود را بنویسید:")
    await state.set_state(TicketStates.waiting_question)

@dp.message(TicketStates.waiting_question)
async def ticket_question(m: types.Message, state: FSMContext):
    data = await state.get_data()
    title, question = data['title'], m.text
    username = m.from_user.username or "ندارد"
    user_id = m.from_user.id

    # ارسال پیام تیکت برای ادمین‌ها
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"""🎫 تیکت جدید:

📌 عنوان: {title}
🆔 کاربر: {username} | {user_id}
💬 پیام: {question}

✅ برای پاسخ دادن به این کاربر، به صورت دستی پیام بده یا سیستم پاسخ‌دهی را پیاده‌سازی کن.
        """)

    await m.answer("✅ تیکت شما با موفقیت ثبت شد. منتظر پاسخ ادمین باشید.")
    await state.clear()

@dp.callback_query(F.data.startswith("replyticket_"))
async def reply_ticket_start(c: types.CallbackQuery, state: FSMContext):
    user_id = int(c.data.split('_')[1])
    await state.update_data(reply_to=user_id)
    await bot.send_message(c.from_user.id, "📝 پیام خود را برای پاسخ وارد کنید:")
    await state.set_state(AdminStates.replying_ticket)

@dp.message(AdminStates.replying_ticket)
async def send_ticket_reply(m: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reply_to")
    try:
        await bot.send_message(user_id, f"""✉️ پاسخ پشتیبانی:

{m.text}
""")
        await m.answer("✅ پاسخ ارسال شد.", reply_markup=admin_menu())
    except:
        await m.answer("❌ ارسال پیام ناموفق بود.", reply_markup=admin_menu())
    await state.clear()


# --- پیام پیش‌فرض ---
@dp.message()
async def fallback(m: types.Message):
    await m.answer("❓ لطفاً از منو استفاده کنید.", reply_markup=main_menu())

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🎫 تیکت جدید از {m.from_user.full_name} ({m.from_user.id}):\n"
                f"📌 عنوان: {title}\n"
                f"📝 سوال: {question}"
            )
        except:
            continue
    await m.answer("✅ تیکت شما ثبت شد. منتظر پاسخ ادمین باشید.", reply_markup=main_menu())
    await state.clear()

# --- نمایش تیکت‌ها برای ادمین ---
@dp.message(F.text == "🎫 تیکت‌های پشتیبانی")
async def view_tickets(m: types.Message):
    if not is_admin(m.from_user.id): return
    tickets = db.get_all_tickets()
    if not tickets:
        await m.answer("📭 تیکتی وجود ندارد.")
        return
    for t in tickets:
        btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ پاسخ", callback_data=f"reply_ticket_{t[0]}")]
        ])
        await m.answer(
            f"🎫 تیکت #{t[0]} از {t[1]}:\n"
            f"📌 عنوان: {t[2]}\n"
            f"📝 متن: {t[3]}", reply_markup=btn)

# --- پاسخ به تیکت ---
@dp.callback_query(F.data.startswith("reply_ticket_"))
async def reply_ticket_cb(c: types.CallbackQuery, state: FSMContext):
    ticket_id = int(c.data.split("_")[-1])
    await state.set_state(AdminStates.replying_ticket)
    await state.update_data(ticket_id=ticket_id)
    await c.message.answer("📝 لطفا پاسخ خود را ارسال کنید:")
    await c.answer()

@dp.message(AdminStates.replying_ticket)
async def process_ticket_reply(m: types.Message, state: FSMContext):
    data = await state.get_data()
    ticket = db.get_ticket_by_id(data['ticket_id'])
    if ticket:
        user_id = ticket[1]
        await bot.send_message(user_id, f"📬 پاسخ تیکت شما:\n{m.text}")
        db.delete_ticket(data['ticket_id'])
        await m.answer("✅ پاسخ ارسال شد.", reply_markup=admin_menu())
    else:
        await m.answer("⛔ تیکت یافت نشد یا قبلاً پاسخ داده شده.", reply_markup=admin_menu())
    await state.clear()

# --- اجرای بات ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())