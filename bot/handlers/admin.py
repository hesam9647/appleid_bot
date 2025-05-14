from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from bot.utils.db import get_stats

async def cmd_stats(message: types.Message):
    stats = get_stats()
    users_count, sales_count, transactions_count = stats
    await message.answer(f"تعداد کاربران: {users_count}\nتعداد فروش‌ها: {sales_count}\nتعداد تراکنش‌ها: {transactions_count}")

from aiogram import types
from bot.utils.db import add_product, get_products

async def cmd_add_product(message: types.Message):
    args = message.text.split(' ', 2)
    if len(args) < 3:
        await message.answer("لطفاً نام و قیمت محصول را وارد کنید.")
        return
    name = args[1]
    price = float(args[2])
    add_product(name, price)
    await message.answer(f"محصول '{name}' با قیمت {price} تومان اضافه شد.")

async def cmd_list_products(message: types.Message):
    products = get_products()
    if products:
        product_list = '\n'.join([f"{product[1]} - {product[2]} تومان" for product in products])
        await message.answer(f"محصولات موجود:\n{product_list}")
    else:
        await message.answer("هیچ محصولی وجود ندارد.")



from bot.utils.db import block_user, unblock_user, get_blocked_users

async def cmd_block_user(message: types.Message):
    user_id = int(message.text.split(' ')[1])
    block_user(user_id)
    await message.answer(f"کاربر با آی‌دی {user_id} مسدود شد.")

async def cmd_unblock_user(message: types.Message):
    user_id = int(message.text.split(' ')[1])
    unblock_user(user_id)
    await message.answer(f"کاربر با آی‌دی {user_id} رفع مسدودیت شد.")
