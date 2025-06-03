from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.database import user_db  # اضافه کن

router = Router()

@router.message(F.text == "🛍 خرید سرویس")
async def buy_service(msg: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 اپل آیدی آماده", callback_data="buy_ready")],
        [InlineKeyboardButton(text="🛒 اپل آیدی سفارشی", callback_data="buy_custom")],
    ])
    await msg.answer("لطفاً نوع سرویس موردنظر را انتخاب کنید:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("buy_"))
async def handle_buy_option(callback: CallbackQuery):
    if callback.data == "buy_ready":
        await callback.message.edit_text("💵 تعرفه اپل آیدی آماده:\n✅ قیمت: 200 هزار تومان\n⏳ تحویل: فوری\n\nبرای ادامه پرداخت، از /pay استفاده کنید.")
    elif callback.data == "buy_custom":
        await callback.message.edit_text("📝 لطفاً اطلاعات سفارشی خود را وارد کنید.")

@router.message(F.text == "/start")
async def start(msg: Message):
    await user_db.register_user(
        user_id=msg.from_user.id,
        username=msg.from_user.username,
        full_name=msg.from_user.full_name
    )
    await msg.answer("🎉 خوش آمدید!\nاز منوی زیر یکی از گزینه‌ها را انتخاب کنید.")
