# bot/handlers/admin.py
from aiogram import types, Dispatcher
from bot.utils.db import get_stats, add_product, get_products, block_user, unblock_user
from aiogram.types import Message

# بررسی ادمین بودن
def is_admin(user_id: int, admins: list):
    return user_id in admins


# نمایش آمار
async def cmd_stats(message: Message, admins: list):
    if not is_admin(message.from_user.id, admins):
        return await message.answer("❌ شما ادمین نیستید.")
    users, sales, txs = await get_stats()
    await message.answer(f"""📊 آمار:
👥 کاربران: {users}
💰 فروش: {sales}
🔁 تراکنش‌ها: {txs}""")

# افزودن محصول
async def cmd_add_product(message: Message, admins: list):
    if not is_admin(message.from_user.id, admins):
        return await message.answer("❌ دسترسی ندارید.")
    args = message.text.split(" ", 2)
    if len(args) < 3:
        return await message.answer("❗️فرمت صحیح: /addproduct نام قیمت")
    name = args[1]
    try:
        price = float(args[2])
    except:
        return await message.answer("❗️قیمت باید عدد باشد.")
    await add_product(name, price)
    await message.answer(f"✅ محصول '{name}' با قیمت {price} اضافه شد.")

# لیست محصولات
async def cmd_list_products(message: Message, admins: list):
    if not is_admin(message.from_user.id, admins):
        return await message.answer("❌ دسترسی ندارید.")
    products = await get_products()
    if not products:
        return await message.answer("❌ هیچ محصولی ثبت نشده است.")
    text = '\n'.join([f"{p[1]} - {p[2]} تومان" for p in products])
    await message.answer(f"📦 محصولات:\n{text}")

# مسدود کردن کاربر
async def cmd_block_user(message: Message, admins: list):
    if not is_admin(message.from_user.id, admins):
        return await message.answer("❌ دسترسی ندارید.")
    try:
        user_id = int(message.text.split()[1])
        await block_user(user_id)
        await message.answer(f"🚫 کاربر {user_id} مسدود شد.")
    except:
        await message.answer("❗️فرمت صحیح: /block user_id")

# آزاد کردن کاربر
async def cmd_unblock_user(message: Message, admins: list):
    if not is_admin(message.from_user.id, admins):
        return await message.answer("❌ دسترسی ندارید.")
    try:
        user_id = int(message.text.split()[1])
        await unblock_user(user_id)
        await message.answer(f"✅ کاربر {user_id} آزاد شد.")
    except:
        await message.answer("❗️فرمت صحیح: /unblock user_id")

# ثبت هندلرها
def register_admin_handlers(dp: Dispatcher, admins: list):
    dp.message.register(lambda m: cmd_stats(m, admins), commands=["stats"])
    dp.message.register(lambda m: cmd_add_product(m, admins), commands=["addproduct"])
    dp.message.register(lambda m: cmd_list_products(m, admins), commands=["listproducts"])
    dp.message.register(lambda m: cmd_block_user(m, admins), commands=["block"])
    dp.message.register(lambda m: cmd_unblock_user(m, admins), commands=["unblock"])
