from aiogram import Router, F
from aiogram.types import Message
import os

router = Router()
admin_ids = list(map(int, os.getenv("ADMIN_IDS").split()))

@router.message(F.from_user.id.in_(admin_ids), F.text == "/panel")
async def admin_panel(msg: Message):
    await msg.answer("🎛 پنل مدیریت فعال است.\nارسال /users برای مدیریت کاربران\nارسال /addapple برای افزودن اپل آیدی جدید")
