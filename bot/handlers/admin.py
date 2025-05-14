from aiogram import types
from aiogram import Router  # تغییر به Router به جای Dispatcher
from aiogram.filters import Command
from bot.utils.db import get_stats, add_product, get_products, block_user, unblock_user
from bot.keyboards.reply import admin_menu

router = Router()  # تعریف Router

def register_admin_handlers(dp):
    admins = dp.admins  # دریافت ادمین‌ها از دیسپچر

    def is_admin(user_id):
        return user_id in admins

    @router.message(Command("admin"))
    async def admin_panel(message: types.Message):
        if not is_admin(message.from_user.id):
            return await message.answer("❌ دسترسی ندارید.")
        await message.answer("🛠 پنل مدیریت:", reply_markup=admin_menu())

    @router.message(Command("stats"))
    async def stats(message: types.Message):
        if not is_admin(message.from_user.id): return
        users, sales, txs = await get_stats()
        await message.answer(f"👥 کاربران: {users}\n💰 فروش: {sales}\n🔁 تراکنش‌ها: {txs}")

    @router.message(Command("addproduct"))
    async def ask_add_product(message: types.Message):
        await message.answer("مثال: /addproduct نام قیمت")

    @router.message(Command("addproduct"))
    async def add_product(message: types.Message):
        if not is_admin(message.from_user.id): return
        args = message.text.split(" ", 2)
        if len(args) < 3:
            return await message.answer("❌ دستور صحیح: /addproduct نام قیمت")
        
        try:
            name, price = args[1], float(args[2])
        except ValueError:
            return await message.answer("❌ قیمت باید یک عدد باشد.")
        
        await add_product(name, price)
        await message.answer(f"✅ '{name}' با قیمت {price} اضافه شد.")

# این خط را در کد خود اضافه کنید تا هندلرها به دیسپچر اضافه شوند
def register_router(dp):
    dp.include_router(router)
