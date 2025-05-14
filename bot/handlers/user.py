from aiogram import types
from aiogram import Router  # تغییر به Router به جای Dispatcher
from aiogram.filters import Command
from bot.utils.db import get_products
from bot.keyboards.inline import product_buttons

router = Router()  # تعریف Router

@router.message(lambda message: message.text == "🛒 خرید اپل آیدی")
async def list_products(message: types.Message):
    products = await get_products()
    if not products:
        return await message.answer("هیچ محصولی موجود نیست.")
    await message.answer("لطفاً یک محصول را انتخاب کنید:", reply_markup=product_buttons(products))

# اضافه کردن router به دیسپچر
def register_router(dp):
    dp.include_router(router)
