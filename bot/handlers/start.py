from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router  # این را وارد کنید

# ایجاد روتری برای هندلرها
router = Router()

# تعریف هندلر شروع
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("سلام، به ربات خوش آمدید!")

# ثبت هندلرها در dp
def register_start_handlers(dp: Dispatcher):
    dp.include_router(router)  # ثبت روتری که شامل هندلرها است
