from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot import config
from bot.utils import db
from bot.keyboards.inline import admin_keyboard, user_manage_keyboard
from bot.states.admin_states import AdminUserWallet

router = Router()

@router.message(F.text == "/admin")
async def admin_panel(message: types.Message):
    if message.from_user.id not in config.ADMINS:
        return await message.answer("❌ شما ادمین نیستید.")
    
    await message.answer("سلام ادمین عزیز، یکی از گزینه‌ها را انتخاب کنید:", reply_markup=admin_keyboard())


@router.callback_query(F.data == "manage_users")
async def ask_user_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("لطفاً آیدی عددی کاربر را وارد کنید:")
    await state.set_state(AdminUserWallet.waiting_for_user_id)
    await callback.answer()


@router.message(AdminUserWallet.waiting_for_user_id)
async def receive_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = db.get_user(user_id)
        if not user:
            await message.answer("❌ کاربری با این آیدی پیدا نشد.")
            return await state.clear()

        balance = db.get_wallet(user_id)
        await state.clear()
        await message.answer(
            f"🔎 اطلاعات کاربر:\n"
            f"👤 نام: {user[1]}\n"
            f"🏷 یوزرنیم: @{user[2] or 'ندارد'}\n"
            f"💰 موجودی فعلی: {balance:,} تومان",
            reply_markup=user_manage_keyboard(user_id)
        )
    except:
        await message.answer("❌ لطفاً آیدی عددی معتبر وارد کنید.")
        await state.clear()


@router.callback_query(F.data.startswith("add_credit:"))
async def ask_amount(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    await state.update_data(target_user=user_id)
    await callback.message.answer("لطفاً مبلغی که می‌خواهید اضافه کنید را وارد کنید:")
    await state.set_state(AdminUserWallet.waiting_for_amount)
    await callback.answer()


@router.message(AdminUserWallet.waiting_for_amount)
async def receive_amount(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        user_id = data["target_user"]
        amount = int(message.text)

        db.update_wallet(user_id, amount)
        new_balance = db.get_wallet(user_id)

        await message.answer(f"✅ {amount:,} تومان به کاربر {user_id} اضافه شد.\n"
                             f"💳 موجودی جدید: {new_balance:,} تومان")
        await state.clear()
    except:
        await message.answer("❌ لطفاً عدد معتبر وارد کنید.")
        await state.clear()

from bot.states.user_states import AdminSupport

@router.callback_query(F.data == "manage_tickets")
async def show_tickets(callback: types.CallbackQuery):
    tickets = db.get_unanswered_tickets()
    if not tickets:
        return await callback.message.answer("📭 تیکت پاسخ‌داده‌نشده‌ای وجود ندارد.")

    await callback.message.answer("📨 لیست تیکت‌های باز:", reply_markup=ticket_list_keyboard(tickets))
    await callback.answer()

@router.callback_query(F.data.startswith("ticket:"))
async def ask_reply(callback: types.CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split(":")[1])
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        return await callback.message.answer("❌ تیکت پیدا نشد.")

    await callback.message.answer(
        f"📨 پیام کاربر:\n{ticket[2]}\n\n🖊 لطفاً پاسخ خود را وارد کنید:"
    )
    await state.set_state(AdminSupport.waiting_for_reply)
    await state.update_data(ticket_id=ticket_id, user_id=ticket[1])
    await callback.answer()

@router.message(AdminSupport.waiting_for_reply)
async def send_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.reply_to_ticket(data["ticket_id"], message.text)

    try:
        await message.bot.send_message(
            chat_id=data["user_id"],
            text=f"📬 پاسخ پشتیبانی:\n{message.text}"
        )
    except:
        pass

    await message.answer("✅ پاسخ شما ارسال شد.")
    await state.clear()
