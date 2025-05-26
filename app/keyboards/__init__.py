from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.keyboards.user_kb import main_menu_kb, wallet_kb
from app.services.user_service import UserService

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌟 به ربات فروش اپل آیدی خوش آمدید!\n"
        "از منوی زیر گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "wallet")
async def show_wallet(callback: CallbackQuery):
    user_service = UserService()
    balance = await user_service.get_balance(callback.from_user.id)
    
    await callback.message.edit_text(
        f"💰 موجودی فعلی شما: {balance:,} تومان\n"
        "از منوی زیر انتخاب کنید:",
        reply_markup=wallet_kb()
    )
