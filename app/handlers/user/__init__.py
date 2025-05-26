from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from app.keyboards.user_kb import main_menu_kb, wallet_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌟 به ربات فروش اپل آیدی خوش آمدید!\n"
        "لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌟 منوی اصلی:\n"
        "لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "wallet")
async def process_wallet(callback: CallbackQuery):
    # Here you should get user's balance from database
    balance = 0  # Placeholder
    await callback.message.edit_text(
        f"💰 موجودی فعلی شما: {balance} تومان\n"
        "برای مدیریت کیف پول خود از دکمه‌های زیر استفاده کنید:",
        reply_markup=wallet_kb()
    )
