from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.keyboards.user_kb import (
    order_kb,
    product_kb,
    product_quantity_kb,
    order_status_kb,
    orders_list_kb
)

router = Router()

class OrderStates(StatesGroup):
    selecting_product = State()
    entering_quantity = State()
    confirming_order = State()

@router.callback_query(F.data == "buy_service")
async def show_products(callback: CallbackQuery):
    product_service = ProductService(callback.bot.get('db_session'))
    products = await product_service.get_active_products()
    
    await callback.message.edit_text(
        "🛍 فروشگاه\n"
        "لطفاً محصول مورد نظر خود را انتخاب کنید:",
        reply_markup=product_kb(products)
    )

@router.callback_query(F.data.startswith("product_"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[1])
    
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "📦 لطفاً تعداد مورد نظر را انتخاب کنید:",
        reply_markup=product_quantity_kb()
    )
    await state.set_state(OrderStates.entering_quantity)

@router.callback_query(OrderStates.entering_quantity, F.data.startswith("quantity_"))
async def process_quantity(callback: CallbackQuery, state: FSMContext):
    quantity = int(callback.data.split('_')[1])
    data = await state.get_data()
    
    product_service = ProductService(callback.bot.get('db_session'))
    product = await product_service.get_product(data['product_id'])
    
    if not product or product.stock < quantity:
        await callback.answer("❌ موجودی کافی نیست!", show_alert=True)
        return
    
    total_price = product.price * quantity
    await state.update_data(quantity=quantity)
    
    await callback.message.edit_text(
        f"🛒 سبد خرید شما:\n\n"
        f"📦 {product.name}\n"
        f"📊 تعداد: {quantity}\n"
        f"💰 قیمت واحد: {product.price:,} تومان\n"
        f"💳 قیمت کل: {total_price:,} تومان\n\n"
        f"آیا سفارش را تأیید می‌کنید؟",
        reply_markup=order_kb()
    )
    await state.set_state(OrderStates.confirming_order)

@router.callback_query(OrderStates.confirming_order, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_service = OrderService(callback.bot.get('db_session'))
    
    order = await order_service.create_order(
        user_id=callback.from_user.id,
        items=[{
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
            reply_markup=order_status_kb(order.id)
        )
    else:
        await callback.message.edit_text(
            "❌ خطا در ثبت سفارش!",
            reply_markup=product_kb(await product_service.get_active_products())
        )
    
    await state.clear()

@router.callback_query(F.data == "purchase_history")
async def show_orders(callback: CallbackQuery):
    order_service = OrderService(callback.bot.get('db_session'))
    orders = await order_service.get_user_orders(callback.from_user.id)
    
    if not orders:
        await callback.message.edit_text(
            "📝 شما هنوز سفارشی ثبت نکرده‌اید!",
            reply_markup=orders_list_kb()
        )
        return
    
    text = "📋 لیست سفارش‌های شما:\n\n"
    for order in orders:
        text += f"🔖 سفارش #{order.id}\n"
        text += f"💳 مبلغ: {order.total_amount:,} تومان\n"
        text += f"📅 تاریخ: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        text += f"🔵 وضعیت: {order.status}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=orders_list_kb()
    )
