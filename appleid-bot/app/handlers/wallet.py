from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.database.wallet_db import get_balance
from app.keyboards.user import wallet_menu
from config import ADMINS
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.wallet_db import add_balance


router = Router()

class WalletState(StatesGroup):
    waiting_receipt = State()

@router.message(F.text == "💰 کیف پول")
async def wallet_main(msg: Message):
    balance = await get_balance(msg.from_user.id)
    await msg.answer(
        f"💼 موجودی شما: {balance:,} تومان",
        reply_markup=wallet_menu()
    )

@router.callback_query(F.data == "add_balance")
async def start_add_balance(call: CallbackQuery):
    await call.message.answer(
        "💳 لطفاً مبلغ را به شماره کارت زیر واریز کنید:\n\n"
        "💳 6037 9917 1234 5678\n"
        "🏦 بانک ملی به نام حسام\n\n"
        "سپس رسید را (به صورت عکس یا متن) ارسال کنید:",
    )
    await call.message.answer("📝 لطفاً رسید را همین‌جا بفرستید.")
    await call.message.bot.set_state(call.from_user.id, "waiting_receipt")


@router.message(WalletState.waiting_receipt)
async def receive_receipt(msg: Message, state: FSMContext):
    await state.clear()

    for admin in ADMINS:
        await msg.forward(admin)
        await msg.bot.send_message(
            admin,
            f"🧾 رسید جدید برای بررسی:\n"
            f"👤 کاربر: {msg.from_user.full_name} (@{msg.from_user.username})\n"
            f"🆔 ID: {msg.from_user.id}\n\n"
            f"برای تأیید و افزایش موجودی:\n"
            f`/confirm_{msg.from_user.id}_AMOUNT`
        )

    await msg.reply("✅ رسید شما ارسال شد. پس از بررسی توسط پشتیبانی، موجودی شما افزایش می‌یابد.")


@router.message(F.text.regexp(r"^/confirm_(\d+)_([0-9]+)"))
async def confirm_balance(msg: Message, regexp: F.text.regexp):
    user_id = int(regexp.group(1))
    amount = int(regexp.group(2))

    await add_balance(user_id, amount, "افزایش توسط ادمین")
    await msg.bot.send_message(user_id, f"✅ مبلغ {amount:,} تومان به کیف پول شما افزوده شد.")
    await msg.answer("✅ موجودی با موفقیت افزایش یافت.")
