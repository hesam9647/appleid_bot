from aiogram import Router, types, F
from app.utils.database import add_user
from keyboards.user_kb import user_main_kb
from config import ADMIN_IDS

router = Router()

@router.message(commands=["start"])
async def cmd_start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username)
    text = f"سلام {message.from_user.full_name}!\nبه ربات فروش اپل‌آیدی خوش آمدید."
    kb = user_main_kb()
    await message.answer(text, reply_markup=kb)

@router.message()
async def check_block(message: types.Message):
    from app.utils.database import is_user_blocked
    if is_user_blocked(message.from_user.id):
        await message.answer("❌ شما از استفاده از ربات بلاک شده‌اید.")
        return
