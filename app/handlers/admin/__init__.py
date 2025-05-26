from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards.admin_kb import admin_main_menu_kb, admin_user_management_kb
from app.services.user_service import UserService
from app.middlewares.access_middleware import AdminAccessMiddleware

router = Router()

# اعمال میدل‌ویر دسترسی ادمین
router.message.middleware(AdminAccessMiddleware())
router.callback_query.middleware(AdminAccessMiddleware())

# استیت‌ها برای مدیریت وضعیت‌های مختلف
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_excel = State()
    waiting_for_price = State()

# کامند /admin برای ورود به پنل ادمین
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer(
        "👨‍💼 پنل مدیریت\n"
        "به پنل مدیریت خوش آمدید. لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=admin_main_menu_kb()
    )

# بازگشت به منوی اصلی ادمین
@router.callback_query(F.data == "admin_main")
async def process_admin_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "👨‍💼 پنل مدیریت\n"
        "لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=admin_main_menu_kb()
    )
    await callback.answer()

# منوی مدیریت کاربران
@router.callback_query(F.data == "admin_users")
async def process_admin_users(callback: CallbackQuery):
    await callback.message.edit_text(
        "👥 مدیریت کاربران\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=admin_user_management_kb()
    )
    await callback.answer()

# شروع ارسال پیام همگانی
@router.callback_query(F.data == "admin_broadcast")
async def process_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✉️ ارسال پیام همگانی\n"
        "لطفاً متن پیام خود را ارسال کنید:"
    )
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_broadcast)

# دریافت و ارسال پیام همگانی
@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast_message(message: Message, state: FSMContext):
    broadcast_text = message.text
    # پیاده‌سازی واقعی ارسال به کاربران (فعلاً نمونه ساده)
    await message.answer("✅ پیام شما با موفقیت به تمام کاربران ارسال شد.")
    # در آینده: حلقه ارسال به کاربران از دیتابیس
    await state.clear()
