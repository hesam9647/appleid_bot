from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.product_service import ProductService
from app.keyboards.admin_kb import admin_products_kb

router = Router()

class ProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_stock = State()

@router.callback_query(F.data == "admin_products")
async def show_products_menu(callback: CallbackQuery):
    product_service = ProductService(callback.bot.get('db_session'))
    products = await product_service.get_active_products()
    
    text = "📦 مدیریت محصولات\n\n"
    for product in products:
        text += f"📌 {product.name}\n"
        text += f"💰 قیمت: {product.base_price:,} تومان\n"
        text += f"📦 موجودی: {product.stock}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_products_kb()
    )

@router.callback_query(F.data == "admin_add_product")
async def add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📦 افزودن محصول جدید\n"
        "لطفاً نام محصول را وارد کنید:"
    )
    await state.set_state(ProductStates.waiting_for_name)
