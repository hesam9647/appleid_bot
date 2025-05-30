from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.filters.admin import AdminFilter
from app.keyboards.admin_kb import admin_main_menu_kb

# Create admin router
admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())

@admin_router.message(Command("admin"))
async def admin_start(message: Message):
    await message.answer(
        "👨‍💼 پنل مدیریت\n"
        "به پنل مدیریت خوش آمدید!\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=admin_main_menu_kb()
    )

# Import admin handlers
from .users import router as users_router
from .products import router as products_router
from .settings import router as settings_router

# Include admin routers
admin_router.include_router(users_router)
admin_router.include_router(products_router)
admin_router.include_router(settings_router)
