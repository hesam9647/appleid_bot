from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.user_service import UserService
from app.keyboards.admin_kb import admin_users_kb, admin_user_actions_kb

router = Router()


class UserStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_note = State()
    waiting_for_balance = State()

@router.callback_query(F.data == "admin_users")
async def show_users_menu(callback: CallbackQuery):
    user_service = UserService(callback.bot.get('db_session'))
    stats = await user_service.get_user_stats()
    
    text = "👥 مدیریت کاربران\n\n"
    text += f"📊 آمار کلی:\n"
    text += f"👤 کل کاربران: {stats['total_users']}\n"
    text += f"✅ فعال: {stats['active_users']}\n"
    text += f"❌ مسدود: {stats['blocked_users']}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_users_kb()
    )

@router.callback_query(F.data == "admin_user_search")
async def search_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 جستجوی کاربر\n"
        "لطفاً شناسه کاربری یا یوزرنیم کاربر مورد نظر را وارد کنید:"
    )
    await state.set_state(UserStates.waiting_for_user_id)

@router.message(UserStates.waiting_for_user_id)
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
        await message.answer(
            "❌ کاربر مورد نظر یافت نشد!",
            reply_markup=admin_users_kb()
        )
        await state.clear()
        return

    text = f"👤 اطلاعات کاربر:\n\n"
    text += f"🆔 شناسه: {user.user_id}\n"
    text += f"👤 نام کاربری: @{user.username}\n"
    text += f"💰 موجودی: {user.balance:,} تومان\n"
    text += f"📅 تاریخ عضویت: {user.created_at.strftime('%Y-%m-%d')}\n"
    text += f"🔄 وضعیت: {'فعال' if not user.is_blocked else '🚫 مسدود'}\n"
    
    await message.answer(
        text,
        reply_markup=admin_user_actions_kb(user.user_id)
    )
    await state.clear()
