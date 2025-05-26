from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.user_kb import (
    apple_id_types_kb,
    confirm_purchase_kb,
    main_menu_kb
)
from app.services.appleid import AppleIDService
from app.services.user_service import UserService

router = Router()

class PurchaseStates(StatesGroup):
    selecting_type = State()
    confirming_purchase = State()

@router.callback_query(F.data == "buy_service")
async def show_apple_id_types(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PurchaseStates.selecting_type)
    await callback.message.edit_text(
        "🔹 لطفا نوع اپل آیدی مورد نظر خود را انتخاب کنید:",
        reply_markup=apple_id_types_kb()
    )

@router.callback_query(PurchaseStates.selecting_type)
async def show_confirmation(callback: CallbackQuery, state: FSMContext, 
                          apple_id_service: AppleIDService):
    apple_id_type = callback.data
    available_id = await apple_id_service.get_available_apple_ids(apple_id_type)
    
    if not available_id:
        await callback.message.edit_text(
            "⚠️ متاسفانه در حال حاضر این نوع اپل آیدی موجود نیست.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return

    apple_id = available_id[0]
    await state.update_data(apple_id_id=apple_id.id, price=apple_id.price)
    
    await callback.message.edit_text(
        f"📱 اطلاعات سفارش:\n"
        f"نوع: {apple_id_type}\n"
        f"قیمت: {apple_id.price:,} تومان\n\n"
        f"آیا مایل به خرید هستید؟",
        reply_markup=confirm_purchase_kb()
    )
    await state.set_state(PurchaseStates.confirming_purchase)

@router.callback_query(PurchaseStates.confirming_purchase)
async def process_purchase(callback: CallbackQuery, state: FSMContext,
                         user_service: UserService, apple_id_service: AppleIDService):
    if callback.data != "confirm_purchase":
        await callback.message.edit_text(
            "❌ خرید لغو شد.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return

    data = await state.get_data()
    apple_id_id = data['apple_id_id']
    price = data['price']

    order = await user_service.create_order(callback.from_user.id, apple_id_id, price)
    if order:
        apple_id = await apple_id_service.mark_as_sold(apple_id_id)
        await callback.message.edit_text(
            f"✅ خرید شما با موفقیت انجام شد!\n\n"
            f"اطلاعات اپل آیدی:\n"
            f"ایمیل: {apple_id.email}\n"
            f"رمز عبور: {apple_id.password}\n\n"
            f"🔐 لطفا اطلاعات را در جای امن ذخیره کنید.",
            reply_markup=main_menu_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ موجودی کافی نیست. لطفا ابتدا کیف پول خود را شارژ کنید.",
            reply_markup=main_menu_kb()
        )
    
    await state.clear()
