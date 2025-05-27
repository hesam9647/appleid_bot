from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.keyboards.user_kb import order_kb, product_kb

router = Router()

class OrderStates(StatesGroup):
    selecting_product = State()
    entering_quantity = State()
    confirming_order = State()

@router.callback_query(F.data == "start_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    product_service = ProductService(callback.bot.get('db_session'))
    products = await product_service.get_active_products()
    
    await callback.message.edit_text(
        "🛍 سفارش جدید\n"
        "لطفاً محصول مورد نظر خود را انتخاب کنید:",
        reply_markup=product_kb(products)
    )
    await state.set_state(OrderStates.selecting_product)

@router.callback_query(OrderStates.selecting_product)
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[1])
    await state.update_data(product_id=product_id)
    
    await callback.message.edit_text(
        "📦 لطفاً تعداد مورد نظر را وارد کنید:"
    )
    await state.set_state(OrderStates.entering_quantity)

@router.message(OrderStates.entering_quantity)
async def enter_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity < 1:
            raise ValueError
            
        data = await state.get_data()
        product_service = ProductService(message.bot.get('db_session'))
        product = await product_service.get_product(data['product_id'])
        
        if not product or product.stock < quantity:
            await message.answer("❌ موجودی کافی نیست!")
            return
            
        total_price = product.base_price * quantity
        
        await state.update_data(quantity=quantity)
        await message.answer(
            f"🛒 سبد خرید شما:\n\n"
            f"📦 {product.name}\n"
            f"📊 تعداد: {quantity}\n"
            f"💰 قیمت واحد: {product.base_price:,} تومان\n"
            f"💳 قیمت کل: {total_price:,} تومان\n\n"
            f"آیا سفارش را تأیید می‌کنید؟",
            reply_markup=order_kb()
        )
        await state.set_state(OrderStates.confirming_order)
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")

@router.callback_query(OrderStates.confirming_order)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    if callback.data != "confirm_order":
        await state.clear()
        await callback.message.edit_text("❌ سفارش لغو شد.")
        return
        
    data = await state.get_data()
    order_service = OrderService(callback.bot.get('db_session'))
    
    order = await order_service.create_order(
        callback.from_user.id,
        [{
            'product_id': data['product_id'],
            'quantity': data['quantity']
        }]
    )
    
    if order:
        await callback.message.edit_text(
            f"✅ سفارش شما با موفقیت ثبت شد!\n"
            f"🔖 شماره سفارش: #{order.id}\n"
            f"💳 مبلغ قابل پرداخت: {order.total_amount:,} تومان\n\n"
            f"لطفاً نسبت به پرداخت اقدام کنید.",
            reply_markup=payment_kb(order.id)
        )
    else:
        await callback.message.edit_text("❌ خطا در ثبت سفارش!")
    
    await state.clear()
