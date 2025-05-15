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
async def manage_users_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("لطفاً آیدی عددی کاربر را وارد کنید:")
    await state.set_state(AdminUserWallet.waiting_for_user_id)
    await callback.answer()

@router.message(AdminUserWallet.waiting_for_user_id)
async def get_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = db.get_user(user_id)
        if not user:
            return await message.answer("❌ کاربر یافت نشد.")
        
        wallet = db.get_wallet(user_id)
        await state.update_data(user_id=user_id)  # ذخیره user_id تو state، پاک نکن

        # دکمه افزودن اعتبار با callback_data حاوی user_id
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💰 افزودن اعتبار", callback_data=f"add_credit:{user_id}")]
        ])

        await message.answer(
            f"👤 اطلاعات کاربر:\n"
            f"🆔 آیدی: {user_id}\n"
            f"👨‍💼 نام: {user[1] or '-'}\n"
            f"💬 یوزرنیم: @{user[2] or 'ندارد'}\n"
            f"💰 موجودی کیف پول: {wallet} تومان",
            reply_markup=keyboard
        )
    except ValueError:
        await message.answer("❗ لطفاً آیدی عددی معتبر وارد کنید.")

@router.callback_query(F.data.startswith("add_credit:"))
async def prompt_amount(callback: types.CallbackQuery, state: FSMContext):
    user_id_str = callback.data.split(":")[1]
    try:
        user_id = int(user_id_str)
    except ValueError:
        return await callback.message.answer("❌ آیدی کاربر نامعتبر است.")
    
    await state.update_data(user_id=user_id)
    await callback.message.answer("لطفاً مبلغ مورد نظر را برای شارژ کیف پول وارد کنید:")
    await state.set_state(AdminUserWallet.waiting_for_amount)
    await callback.answer()

@router.message(AdminUserWallet.waiting_for_amount)
async def add_amount_to_wallet(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        user_id = data.get("user_id")
        if not user_id:
            return await message.answer("❌ مشکلی پیش آمده، دوباره تلاش کنید.")
        
        amount = int(message.text)
        db.update_wallet(user_id, amount)
        new_balance = db.get_wallet(user_id)
        await message.answer(f"✅ مبلغ {amount} تومان به کیف پول کاربر {user_id} افزوده شد.\n💰 موجودی جدید: {new_balance} تومان")
        await state.clear()
    except ValueError:
        await message.answer("❗ لطفاً فقط عدد وارد کنید.")
