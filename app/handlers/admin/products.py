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
    await callback.message.edit_text(
        "📦 مدیریت محصولات\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=admin_products_kb()
    )
