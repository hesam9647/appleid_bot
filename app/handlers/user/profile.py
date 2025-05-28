from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.keyboards.user_kb import profile_kb

router = Router()

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user = callback.bot.get('user')
    
    text = f"👤 پروفایل شما:\n\n"
    text += f"🆔 شناسه: {user.user_id}\n"
    text += f"💰 موجودی: {user.balance:,} تومان\n"
    text += f"📅 تاریخ عضویت: {user.created_at.strftime('%Y-%m-%d')}"
    
    await callback.message.edit_text(
        text,
        reply_markup=profile_kb()
    )
