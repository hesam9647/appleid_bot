from aiogram import Router, types, F
from keyboards.admin_kb import admin_main_kb, users_list_kb, user_manage_kb, apple_ids_manage_kb, toggle_service_kb, payment_approve_kb
from app.utils.database import get_all_users_info, block_user, is_user_blocked, add_apple_id, get_setting, set_setting, get_available_apple_id, mark_apple_id_sold, add_purchase, get_all_users
from config import ADMIN_IDS
import asyncio

router = Router()

def admin_only(handler):
    async def wrapper(event):
        if event.from_user.id not in ADMIN_IDS:
            await event.answer("❌ دسترسی فقط برای ادمین‌ها مجاز است.")
            return
        await handler(event)
    return wrapper

@router.message(admin_only)
async def admin_start(message: types.Message):
    kb = admin_main_kb()
    await message.answer("پنل مدیریت:", reply_markup=kb)

@router.callback_query(admin_only, F.data == "admin_main")
async def admin_main_menu(call: types.CallbackQuery):
    kb = admin_main_kb()
    await call.message.edit_text("پنل مدیریت:", reply_markup=kb)

@router.callback_query(admin_only, F.data == "admin_users")
async def admin_users_list(call: types.CallbackQuery):
    users = get_all_users_info()
    kb = users_list_kb(users)
    await call.message.edit_text("لیست کاربران:", reply_markup=kb)

@router.callback_query(admin_only, F.data.startswith("user_"))
async def admin_user_manage(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    blocked = is_user_blocked(user_id)
    kb = user_manage_kb(user_id, blocked)
    await call.message.edit_text(f"مدیریت کاربر {user_id}:", reply_markup=kb)

@router.callback_query(admin_only, F.data.startswith("block_"))
async def admin_block_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    block_user(user_id, True)
    await call.answer("کاربر بلاک شد.")
    await admin_users_list(call)

@router.callback_query(admin_only, F.data.startswith("unblock_"))
async def admin_unblock_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    block_user(user_id, False)
    await call.answer("کاربر از بلاک خارج شد.")
    await admin_users_list(call)

@router.callback_query(admin_only, F.data == "