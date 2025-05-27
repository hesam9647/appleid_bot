from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.utils.admin_filters import IsAdmin
from app.services.user_service import UserService
from app.services.stats_service import StatsService
from app.keyboards.admin_kb import (
    admin_main_kb, 
    admin_users_kb,
    admin_broadcast_kb,
    admin_settings_kb
)

router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_user_note = State()
    waiting_for_balance_amount = State()

@router.message(Command("admin"), IsAdmin(admin_ids=[]))  # admin_ids will be filled from config
async def admin_panel(message: Message):
    stats_service = StatsService(message.bot.get('db_session'))
    user_stats = await stats_service.get_user_stats()
    sales_stats = await stats_service.get_sales_stats(days=1)  # Today's stats

    text = "👨‍💼 پنل مدیریت\n\n"
    text += f"📊 آمار امروز:\n"
    text += f"💰 فروش: {sales_stats['total_sales']:,} تومان\n"
    text += f"📦 تعداد فروش: {sales_stats['total_count']}\n\n"
    text += f"👥 کاربران کل: {user_stats['total_users']}\n"
    text += f"✅ کاربران فعال: {user_stats['active_users']}\n"
    text += f"💬 تیکت‌های باز: {await stats_service.get_support_stats()['open_tickets']}\n"

    await message.answer(text, reply_markup=admin_main_kb())

@router.callback_query(F.data == "admin_users_manage")
async def admin_users_management(callback: CallbackQuery):
    user_service = UserService(callback.bot.get('db_session'))
    stats = await user_service.get_user_stats()

    text = "👥 مدیریت کاربران\n\n"
    text += f"📊 آمار کلی:\n"
    text += f"👤 کل کاربران: {stats['total_users']}\n"
    text += f"✅ فعال: {stats['active_users']}\n"
    text += f"❌ مسدود: {stats['blocked_users']}\n"
    text += f"💰 دارای تراکنش: {stats['users_with_transaction']}"

    await callback.message.edit_text(text, reply_markup=admin_users_kb())

@router.callback_query(F.data == "admin_user_search")
async def admin_search_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 جستجوی کاربر\n"
        "لطفاً شناسه کاربری یا یوزرنیم کاربر مورد نظر را وارد کنید:"
    )
    await state.set_state(AdminStates.waiting_for_user_id)

@router.message(AdminStates.waiting_for_user_id)
async def process_user_search(message: Message, state: FSMContext):
    user_service = UserService(message.bot.get('db_session'))
    
    try:
        # Try to find by ID first
        user_id = int(message.text)
        user = await user_service.get_user(user_id)
    except ValueError:
        # If not ID, search by username
        user = await user_service.get_user_by_username(message.text.lstrip('@'))

    if not user:
        await message.answer("❌ کاربر مورد نظر یافت نشد!")
        await state.clear()
        return

    text = f"👤 اطلاعات کاربر:\n\n"
    text += f"🆔 شناسه: {user.user_id}\n"
    text += f"👤 نام کاربری: @{user.username}\n"
    text += f"💰 موجودی: {user.balance:,} تومان\n"
    text += f"📅 تاریخ عضویت: {user.created_at.strftime('%Y-%m-%d')}\n"
    text += f"🔄 وضعیت: {'فعال' if not user.is_blocked else '🚫 مسدود'}\n"
    
    if user.note:
        text += f"\n📝 یادداشت:\n{user.note}"

    await message.answer(text, reply_markup=admin_user_actions_kb(user.user_id))
    await state.clear()

@router.callback_query(F.data.startswith("admin_user_block_"))
async def admin_block_user(callback: CallbackQuery):
    user_id = int(callback.data.split('_')[-1])
    user_service = UserService(callback.bot.get('db_session'))
    
    if await user_service.block_user(user_id):
        await callback.answer("✅ کاربر با موفقیت مسدود شد.")
    else:
        await callback.answer("❌ خطا در مسدود کردن کاربر!", show_alert=True)

@router.callback_query(F.data.startswith("admin_user_unblock_"))
async def admin_unblock_user(callback: CallbackQuery):
    user_id = int(callback.data.split('_')[-1])
    user_service = UserService(callback.bot.get('db_session'))
    
    if await user_service.unblock_user(user_id):
        await callback.answer("✅ کاربر با موفقیت آزاد شد.")
    else:
        await callback.answer("❌ خطا در آزاد کردن کاربر!", show_alert=True)

@router.callback_query(F.data.startswith("admin_user_note_"))
async def admin_add_note(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[-1])
    await state.update_data(target_user_id=user_id)
    
    await callback.message.edit_text(
        "📝 افزودن یادداشت\n"
        "لطفاً متن یادداشت را وارد کنید:"
    )
    await state.set_state(AdminStates.waiting_for_user_note)

@router.message(AdminStates.waiting_for_user_note)
async def process_user_note(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['target_user_id']
    
    user_service = UserService(message.bot.get('db_session'))
    if await user_service.add_note(user_id, message.text):
        await message.answer("✅ یادداشت با موفقیت ذخیره شد.")
    else:
        await message.answer("❌ خطا در ذخیره یادداشت!")
    
    await state.clear()
