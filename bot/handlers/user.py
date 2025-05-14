from aiogram import types
from bot.keyboards.default import get_main_keyboard
from bot.utils.db import get_products

def register_user_handlers(dp):

    @dp.message_handler(commands=["start"])
    async def cmd_start(message: types.Message):
        await message.answer("سلام! خوش آمدید. انتخاب کنید:", reply_markup=get_main_keyboard())

    @dp.callback_query_handler(lambda c: c.data == "view_products")
    async def process_view_products(callback_query: types.CallbackQuery):
        products = await get_products()
        if not products:
            await callback_query.message.answer("هیچ محصولی وجود ندارد.")
            return
        product_list = '\n'.join([f"{product[1]} - {product[2]} تومان" for product in products])
        await callback_query.message.answer(f"📦 محصولات:\n{product_list}")

    @dp.callback_query_handler(lambda c: c.data == "support")
    async def process_support(callback_query: types.CallbackQuery):
        await callback_query.message.answer("برای پشتیبانی با ما تماس بگیرید.")
