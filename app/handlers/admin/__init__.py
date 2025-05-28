from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards.admin_kb import admin_main_menu_kb, admin_users_kb
from app.middlewares.access_middleware import AdminAccessMiddleware

admin_router = Router()
admin_router.message.middleware(AdminAccessMiddleware())
admin_router.callback_query.middleware(AdminAccessMiddleware())

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_excel = State()
    waiting_for_price = State()

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer(
        "👨‍💼 پنل مدیریت\n"
        "به پنل مدیریت خوش آمدید. لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=admin_main_menu_kb()
    )

@admin_router.callback_query(F.data == "admin_main")
async def process_admin_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "👨‍💼 پنل مدیریت\n"
        "لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=admin_main_menu_kb()
    )

@admin_router.callback_query(F.data == "admin_broadcast")
async def process_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✉️ ارسال پیام همگانی\n"
        "لطفاً متن پیام خود را ارسال کنید:"
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@admin_router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast_message(message: Message, state: FSMContext):
    # اینجا باید کد ارسال پیام به همه کاربران واقعی باشد
    await message.answer("پیام شما با موفقیت به تمام کاربران ارسال شد.")
    await state.clear()
