# app/handlers/user/products.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.product_service import ProductService
from app.keyboards.user_kb import product_kb, main_menu_kb

router = Router()

class ProductStates(StatesGroup):
    viewing_product = State()
    selecting_category = State()
    searching = State()  # اضافه کردن state جستجو

@router.callback_query(F.data == "products")
async def show_products(callback: CallbackQuery):
    product_service = ProductService(callback.bot.get('db_session'))
    products = await product_service.get_active_products()
    
    if not products:
        await callback.message.edit_text(
            "❌ در حال حاضر محصولی موجود نیست!",
            reply_markup=main_menu_kb()
        )
        return
    
    text = "📦 محصولات موجود:\n\n"
    for product in products:
        text += f"🔸 {product.name}\n"
        text += f"💰 قیمت: {product.price:,} تومان\n"
        if product.description:
            text += f"📝 {product.description}\n"
        text += f"📦 موجودی: {product.stock}\n\n"
    
    # Add search button to keyboard
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔍 جستجو", callback_data="search_product")
    keyboard.button(text="🔙 بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(
        text,
        reply_markup=product_kb(products, keyboard)
    )

@router.callback_query(F.data.startswith("product_view_"))
async def view_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[2])
    product_service = ProductService(callback.bot.get('db_session'))
    product = await product_service.get_product(product_id)
    
    if not product:
        await callback.answer("❌ محصول مورد نظر یافت نشد!", show_alert=True)
        return
    
    text = f"🔸 {product.name}\n\n"
    text += f"💰 قیمت: {product.price:,} تومان\n"
    if product.description:
        text += f"📝 توضیحات: {product.description}\n"
    text += f"📦 موجودی: {product.stock}\n"
    
    keyboard = InlineKeyboardBuilder()
    if product.stock > 0:
        keyboard.button(text="🛒 خرید", callback_data=f"product_{product.id}")
    keyboard.button(text="🔙 بازگشت", callback_data="products")
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(ProductStates.viewing_product)

@router.callback_query(F.data == "search_product")
async def search_products(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 جستجوی محصول\n"
        "لطفاً نام محصول مورد نظر خود را وارد کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="products")]
        ])
    )
    await state.set_state(ProductStates.searching)

@router.message(ProductStates.searching)
async def process_product_search(message: Message, state: FSMContext):
    product_service = ProductService(message.bot.get('db_session'))
    products = await product_service.search_products(message.text)
    
    if not products:
        await message.answer(
            "❌ محصولی با این نام یافت نشد!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت به محصولات", callback_data="products")]
            ])
        )
        await state.clear()
        return
    
    text = "🔍 نتایج جستجو:\n\n"
    for product in products:
        text += f"🔸 {product.name}\n"
        text += f"💰 قیمت: {product.price:,} تومان\n"
        if product.description:
            text += f"📝 {product.description}\n"
        text += f"📦 موجودی: {product.stock}\n\n"
    
    await message.answer(
        text,
        reply_markup=product_kb(products)
    )
    await state.clear()

@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[1])
    product_service = ProductService(callback.bot.get('db_session'))
    products = await product_service.get_products_by_category(category_id)
    
    if not products:
        await callback.message.edit_text(
            "❌ در این دسته‌بندی محصولی موجود نیست!",
            reply_markup=main_menu_kb()
        )
        return
    
    text = "📦 محصولات این دسته:\n\n"
    for product in products:
        text += f"🔸 {product.name}\n"
        text += f"💰 قیمت: {product.price:,} تومان\n"
        if product.description:
            text += f"📝 {product.description}\n"
        text += f"📦 موجودی: {product.stock}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=product_kb(products)
    )

products_router = router
