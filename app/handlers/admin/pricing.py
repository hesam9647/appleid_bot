from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from app.services.price_service import PriceService
from app.services.discount_service import DiscountService
from app.keyboards.admin_kb import admin_pricing_kb

router = Router()

class PriceStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()

class DiscountStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_type = State()
    waiting_for_value = State()
    waiting_for_max_uses = State()
    waiting_for_expiry = State()

@router.callback_query(F.data == "admin_prices")
async def process_prices_menu(callback: CallbackQuery):
    price_service = PriceService(callback.bot.get('db_session'))
    prices = await price_service.get_active_prices()
    
    text = "🏷 تعرفه‌های فعال:\n\n"
    for price in prices:
        text += f"📌 {price.title}\n"
        text += f"💰 {price.price:,} تومان\n"
        text += f"📝 {price.description}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_pricing_kb()
    )

@router.callback_query(F.data == "admin_add_price")
async def process_add_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🏷 افزودن تعرفه جدید\n"
        "لطفاً عنوان تعرفه را وارد کنید:"
    )
    await state.set_state(PriceStates.waiting_for_title)

@router.message(PriceStates.waiting_for_title)
async def process_price_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("لطفاً توضیحات تعرفه را وارد کنید:")
    await state.set_state(PriceStates.waiting_for_description)

@router.message(PriceStates.waiting_for_description)
async def process_price_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("لطفاً قیمت را به تومان وارد کنید:")
    await state.set_state(PriceStates.waiting_for_price)

@router.message(PriceStates.waiting_for_price)
async def process_price_amount(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        data = await state.get_data()
        
        price_service = PriceService(message.bot.get('db_session'))
        await price_service.add_price(
            title=data['title'],
            description=data['description'],
            price=price
        )
        
        await message.answer("✅ تعرفه جدید با موفقیت اضافه شد.")
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
    finally:
        await state.clear()

@router.callback_query(F.data == "admin_discounts")
async def process_discounts_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎁 مدیریت کدهای تخفیف\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=admin_discount_kb()
    )

@router.callback_query(F.data == "admin_add_discount")
async def process_add_discount(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎁 افزودن کد تخفیف جدید\n"
        "لطفاً کد تخفیف را وارد کنید:"
    )
    await state.set_state(DiscountStates.waiting_for_code)
