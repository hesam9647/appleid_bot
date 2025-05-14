from aiogram import types, F, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.utils.db import get_stats, add_product, get_products, block_user, unblock_user
from bot.config import ADMINS


# ⚙️ دکمه‌های پنل ادمین
def get_admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار کلی", callback_data="admin_stats")],
        [InlineKeyboardButton(text="➕ افزودن محصول", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="📦 لیست محصولات", callback_data="admin_list_products")],
        [InlineKeyboardButton(text="⛔ مسدود کردن کاربر", callback_data="admin_block_user")],
        [InlineKeyboardButton(text="✅ رفع مسدودیت", callback_data="admin_unblock_user")],
    ])


# 📍 دستور /admin برای باز کردن پنل
async def cmd_admin_panel(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("❌ شما ادمین نیستید.")
    await message.answer("📍 به پنل مدیریت خوش آمدید:", reply_markup=get_admin_panel_keyboard())


# 📊 آمار
async def cmd_stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("❌ شما ادمین نیستید.")
    users_count, sales_count, transactions_count = get_stats()
    await message.answer(f"تعداد کاربران: {users_count}\n"
                         f"تعداد فروش‌ها: {sales_count}\n"
                         f"تعداد تراکنش‌ها: {transactions_count}")


# ➕ افزودن محصول
async def cmd_add_product(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    args = message.text.split(' ', 2)
    if len(args) < 3:
        return await message.answer("لطفاً به‌صورت `/addproduct نام قیمت` وارد کنید.")
    try:
        name = args[1]
        price = float(args[2])
        add_product(name, price)
        await message.answer(f"✅ محصول '{name}' با قیمت {price} تومان اضافه شد.")
    except ValueError:
        await message.answer("⚠️ قیمت نامعتبر است.")


# 📦 لیست محصولات
async def cmd_list_products(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    products = get_products()
    if not products:
        await message.answer("هیچ محصولی وجود ندارد.")
    else:
        text = "\n".join([f"{p[1]} - {p[2]} تومان" for p in products])
        await message.answer(f"📦 محصولات:\n{text}")


# ⛔ بلاک کاربر
async def cmd_block_user(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    try:
        user_id = int(message.text.split(' ')[1])
        block_user(user_id)
        await message.answer(f"⛔ کاربر {user_id} مسدود شد.")
    except:
        await message.answer("لطفاً آیدی عددی کاربر را وارد کنید.")


# ✅ رفع بلاک
async def cmd_unblock_user(message: types.Message):
    if message.from_user.id not in ADMINS:
        return
    try:
        user_id = int(message.text.split(' ')[1])
        unblock_user(user_id)
        await message.answer(f"✅ کاربر {user_id} آزاد شد.")
    except:
        await message.answer("لطفاً آیدی عددی کاربر را وارد کنید.")


# 🎯 هندلر دکمه‌های پنل ادمین
async def process_admin_buttons(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return await callback.answer("شما ادمین نیستید.", show_alert=True)

    data = callback.data
    msg = callback.message

    if data == "admin_stats":
        await cmd_stats(msg)
    elif data == "admin_add_product":
        await msg.answer("لطفاً از دستور /addproduct نام قیمت استفاده کنید.")
    elif data == "admin_list_products":
        await cmd_list_products(msg)
    elif data == "admin_block_user":
        await msg.answer("لطفاً از دستور /block [user_id] استفاده کنید.")
    elif data == "admin_unblock_user":
        await msg.answer("لطفاً از دستور /unblock [user_id] استفاده کنید.")

    await callback.answer()


# 📌 ثبت هندلرها
def register_admin_handlers(dp: Dispatcher):
    dp.message.register(cmd_admin_panel, commands=["admin"])
    dp.message.register(cmd_stats, commands=["stats"])
    dp.message.register(cmd_add_product, commands=["addproduct"])
    dp.message.register(cmd_list_products, commands=["listproducts"])
    dp.message.register(cmd_block_user, commands=["block"])
    dp.message.register(cmd_unblock_user, commands=["unblock"])
    dp.callback_query.register(process_admin_buttons, F.data.startswith("admin_"))
