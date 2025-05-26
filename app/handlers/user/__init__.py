from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from app.keyboards.user_kb import main_menu_kb, wallet_kb

router = Router()

# /start command
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌟 به ربات فروش اپل آیدی خوش آمدید!\n"
        "لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_kb()
    )

# بازگشت به منوی اصلی
@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌟 منوی اصلی:\n"
        "لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu_kb()
    )

# کیف پول
@router.callback_query(F.data == "wallet")
async def process_wallet(callback: CallbackQuery):
    balance = 0  # در آینده از دیتابیس بگیر
    await callback.message.edit_text(
        f"💰 موجودی فعلی شما: {balance} تومان\n"
        "برای مدیریت کیف پول خود از دکمه‌های زیر استفاده کنید:",
        reply_markup=wallet_kb()
    )

# خرید سرویس
@router.callback_query(F.data == "buy_service")
async def process_buy_service(callback: CallbackQuery):
    await callback.message.edit_text("🛍 برای خرید سرویس، لطفاً یکی از گزینه‌های زیر را انتخاب کنید.")
    await callback.answer()

# تیکت و پشتیبانی
@router.callback_query(F.data == "support")
async def process_support(callback: CallbackQuery):
    await callback.message.edit_text("💬 لطفاً سوال یا مشکل خود را ارسال کنید. پشتیبانی در اسرع وقت پاسخ می‌دهد.")
    await callback.answer()

# راهنما
@router.callback_query(F.data == "help")
async def process_help(callback: CallbackQuery):
    await callback.message.edit_text("📚 راهنمای استفاده از ربات:\n۱. ابتدا کیف پول را شارژ کنید\n۲. سپس سرویس را خریداری کنید...")
    await callback.answer()

# سوابق خرید
@router.callback_query(F.data == "purchase_history")
async def process_purchase_history(callback: CallbackQuery):
    await callback.message.edit_text("🧾 شما هنوز هیچ خریدی انجام نداده‌اید.")
    await callback.answer()

# کد هدیه
@router.callback_query(F.data == "gift_code")
async def process_gift_code(callback: CallbackQuery):
    await callback.message.edit_text("🎁 لطفاً کد هدیه خود را وارد کنید:")
    await callback.answer()

# تعرفه‌ها
@router.callback_query(F.data == "prices")
async def process_prices(callback: CallbackQuery):
    await callback.message.edit_text(
        "📊 تعرفه سرویس‌ها:\n"
        "✔️ اپل آیدی آمریکا دائمی: ۱۵۰,۰۰۰ تومان\n"
        "✔️ اپل آیدی با ایمیل شخصی: ۱۸۰,۰۰۰ تومان\n"
        "✔️ تحویل فوری، قابل استفاده در تمام دیوایس‌ها"
    )
    await callback.answer()
