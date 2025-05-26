import os
from aiogram import Router, types, F, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import pandas as pd
from database import cursor, conn
from keyboards.admin_kb import (
    admin_main_kb, users_list_kb, user_manage_kb,
    apple_ids_manage_kb, toggle_service_kb, payment_approve_kb,
    tickets_list_kb, ticket_reply_kb
)
from app.utils.database import (
    get_all_users_info, block_user, is_user_blocked,
    get_all_tickets, get_ticket_by_id, reply_to_ticket,
    get_setting, set_setting
)
from config import ADMIN_IDS

router = Router()

# دکوراتور برای محدود کردن دسترسی فقط به ادمین‌ها
def admin_only(handler):
    async def wrapper(event, *args, **kwargs):
        user_id = None
        if isinstance(event, types.Message):
            user_id = event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id
        else:
            # در صورت رویدادهای دیگر (مثلاً InlineQuery و غیره) اجازه نمی‌دهیم
            return

        if user_id not in ADMIN_IDS:
            if isinstance(event, types.Message):
                await event.answer("❌ دسترسی فقط برای ادمین‌ها مجاز است.")
            elif isinstance(event, types.CallbackQuery):
                await event.answer("❌ دسترسی فقط برای ادمین‌ها مجاز است.", show_alert=True)
            return
        return await handler(event, *args, **kwargs)
    return wrapper

# -- استارت پنل مدیریت --
@router.message(admin_only)
async def admin_start(message: types.Message):
    kb = admin_main_kb()
    await message.answer("پنل مدیریت:", reply_markup=kb)

@router.callback_query(admin_only, F.data == "admin_main")
async def admin_main_menu(call: types.CallbackQuery):
    kb = admin_main_kb()
    await call.message.edit_text("پنل مدیریت:", reply_markup=kb)

# -- مدیریت کاربران --
@router.callback_query(admin_only, F.data == "admin_users")
async def admin_users_list(call: types.CallbackQuery):
    users = get_all_users_info()
    kb = users_list_kb(users)
    await call.message.edit_text("لیست کاربران:", reply_markup=kb)

@router.callback_query(admin_only, F.data.startswith("user_"))
async def admin_user_manage(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    blocked = is_user_blocked(user_id)
    kb = user_manage_kb(user_id, blocked)
    await call.message.edit_text(f"مدیریت کاربر {user_id}:", reply_markup=kb)

@router.callback_query(admin_only, F.data.startswith("block_"))
async def admin_block_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    block_user(user_id, True)
    await call.answer("کاربر بلاک شد.")
    await admin_users_list(call)

@router.callback_query(admin_only, F.data.startswith("unblock_"))
async def admin_unblock_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    block_user(user_id, False)
    await call.answer("کاربر از بلاک خارج شد.")
    await admin_users_list(call)

# -- مدیریت تیکت‌ها --
class TicketReplyState(StatesGroup):
    waiting_for_reply = State()

@router.callback_query(admin_only, F.data == "admin_tickets")
async def show_tickets(call: types.CallbackQuery):
    tickets = get_all_tickets()
    kb = tickets_list_kb(tickets)
    await call.message.edit_text("📩 لیست تیکت‌های کاربران:", reply_markup=kb)

@router.callback_query(admin_only, F.data.startswith("ticket_"))
async def view_ticket(call: types.CallbackQuery):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if ticket:
        # ساختار تیکت: (id, user_id, message, reply, status, created_at)
        _, user_id, message_text, reply, status, created_at = ticket
        text = (
            f"👤 کاربر: {user_id}\n"
            f"🕓 تاریخ: {created_at}\n\n"
            f"📩 پیام:\n{message_text}\n\n"
            f"✏️ پاسخ:\n{reply if reply else 'هنوز پاسخ داده نشده'}"
        )
        kb = ticket_reply_kb(ticket_id)
        await call.message.edit_text(text, reply_markup=kb)
    else:
        await call.answer("❌ تیکت پیدا نشد.", show_alert=True)

@router.callback_query(admin_only, F.data.startswith("reply_"))
async def start_reply_ticket(call: types.CallbackQuery, state: FSMContext):
    ticket_id = int(call.data.split("_")[1])
    await state.set_state(TicketReplyState.waiting_for_reply)
    await state.update_data(ticket_id=ticket_id)
    await call.message.answer("✍️ پاسخ خود را وارد کنید:")

@router.message(TicketReplyState.waiting_for_reply)
async def send_reply_to_user(message: types.Message, state: FSMContext, bot: types.Bot):
    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await message.answer("❌ تیکت پیدا نشد.")
        await state.clear()
        return

    reply_text = message.text
    reply_to_ticket(ticket_id, reply_text)

    user_id = ticket[1]  # user_id در اندیس ۱
    await bot.send_message(user_id, f"✅ پاسخ پشتیبانی به تیکت شما:\n\n{reply_text}")
    await message.answer("✅ پاسخ با موفقیت ارسال شد.")
    await state.clear()

# -- آپلود فایل اکسل اپل‌آیدی‌ها --
@router.message(admin_only, commands=['upload_apple_ids'])
async def upload_apple_ids(message: types.Message):
    await message.reply("لطفا فایل اکسل اپل‌آیدی‌ها را ارسال کنید.")

@router.message(admin_only, content_types=types.ContentType.DOCUMENT)
async def handle_excel_file(message: types.Message):
    if not message.document.file_name.endswith(('.xls', '.xlsx')):
        await message.reply("❌ فقط فایل اکسل با پسوند .xls یا .xlsx پذیرفته می‌شود.")
        return

    # مسیر ذخیره فایل (مطمئن شوید پوشه app/data وجود دارد)
    file_dir = os.path.join(os.getcwd(), 'app', 'data')
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, message.document.file_name)

    await message.document.download(destination_file=file_path)

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        await message.reply("❌ خطا در خواندن فایل اکسل. مطمئن شوید فایل معتبر است.")
        return

    required_columns = {'apple_id', 'price', 'location'}
    if not required_columns.issubset(df.columns):
        await message.reply("❌ فایل اکسل باید ستون‌های 'apple_id', 'price', و 'location' را داشته باشد.")
        return

    count_added = 0
    for _, row in df.iterrows():
        try:
            cursor.execute(
                "INSERT INTO apple_ids (apple_id, price, location, sold) VALUES (?, ?, ?, 0)",
                (row['apple_id'], row['price'], row['location'])
            )
            count_added += 1
        except Exception as e:
            # ممکنه رکورد تکراری یا خطای دیگه باشه، ردش کن
            pass
    conn.commit()
    await message.reply(f"✅ {count_added} اپل‌آیدی جدید اضافه شد.")

# تابع ثبت هندلرها در Dispatcher
def register_handlers_admin(dp: Dispatcher):
    dp.include_router(router)
