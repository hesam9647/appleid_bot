from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.payment_service import PaymentService
from app.keyboards.user_kb import payment_kb

router = Router()  # ✅ این خط بسیار مهم است

class PaymentStates(StatesGroup):
    waiting_for_amount = State()

@router.callback_query(F.data == "deposit")
async def process_deposit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 شارژ کیف پول\n"
        "لطفاً مبلغ مورد نظر را به تومان وارد کنید:",
        reply_markup=payment_kb()
    )
    await state.set_state(PaymentStates.waiting_for_amount)

@router.message(PaymentStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount < 10000:
            await message.answer("❌ حداقل مبلغ شارژ 10,000 تومان است.")
            return

        payment_service = PaymentService(
            message.bot.get('db_session'),
            merchant_id=message.bot.get('config').payment.merchant_id,
            callback_url=message.bot.get('config').payment.callback_url
        )

        result = await payment_service.create_payment(
            user_id=message.from_user.id,
            amount=amount,
            description=f"شارژ کیف پول - کاربر {message.from_user.id}"
        )

        if result:
            await message.answer(
                f"🔄 در حال انتقال به درگاه پرداخت...\n"
                f"💰 مبلغ: {amount:,} تومان\n\n"
                f"🔗 لینک پرداخت:\n{result['payment_url']}"
            )
        else:
            await message.answer("❌ خطا در ایجاد لینک پرداخت. لطفاً مجدداً تلاش کنید.")

    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
    finally:
        await state.clear()

# ✅ این خط برای اینکه در init.py بتونی با اسم payment_router ایمپورت کنی
payment_router = router
