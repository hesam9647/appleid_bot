from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.user_kb import wallet_kb, payment_methods_kb
from app.services.user_service import UserService

router = Router()

class TopUpStates(StatesGroup):
    entering_amount = State()
    selecting_payment = State()
    waiting_payment = State()

@router.callback_query(F.data == "add_funds")
async def request_amount(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 لطفا مبلغ مورد نظر برای شارژ کیف پول را وارد کنید (به تومان):",
        reply_markup=None
    )
    await state.set_state(TopUpStates.entering_amount)

@router.message(TopUpStates.entering_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount < 10000:  # حداقل مبلغ شارژ
            await message.answer(
                "⚠️ حداقل مبلغ شارژ 10,000 تومان می‌باشد.",
                reply_markup=wallet_kb()
            )
            await state.clear()
            return

        await state.update_data(amount=amount)
        await message.answer(
            f"💳 لطفا روش پرداخت را انتخاب کنید:\n"
            f"مبلغ: {amount:,} تومان",
            reply_markup=payment_methods_kb()
        )
        await state.set_state(TopUpStates.selecting_payment)
        
    except ValueError:
        await message.answer(
            "⚠️ لطفا یک عدد معتبر وارد کنید.",
            reply_markup=wallet_kb()
        )
        await state.clear()

@router.callback_query(TopUpStates.selecting_payment)
async def process_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    
    # اینجا باید به درگاه پرداخت متصل شود
    # فعلا فقط اطلاعات کارت را نمایش می‌دهیم
    await callback.message.edit_text(
        f"🏦 اطلاعات واریز:\n\n"
        f"شماره کارت: 6037-XXXX-XXXX-XXXX\n"
        f"به نام: نام صاحب کارت\n"
        f"مبلغ: {amount:,} تومان\n\n"
        f"پس از واریز، تصویر رسید را ارسال کنید.",
        reply_markup=None
    )
    await state.set_state(TopUpStates.waiting_payment)
