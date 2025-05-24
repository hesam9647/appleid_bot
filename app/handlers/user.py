from aiogram import Router, types, F
from keyboards.user_kb import user_main_kb, buy_service_kb, wallet_kb, purchase_history_kb, help_kb
from app.utils.database import get_wallet, update_wallet, get_purchases, add_purchase, get_available_apple_id, mark_apple_id_sold
from config import ADMIN_IDS

router = Router()

@router.callback_query(F.data == "user_main")
async def user_main_menu(call: types.CallbackQuery):
    kb = user_main_kb()
    await call.message.edit_text("پنل کاربری شما:", reply_markup=kb)

@router.callback_query(F.data == "buy_service")
async def buy_service_menu(call: types.CallbackQuery):
    kb = buy_service_kb()
    await call.message.edit_text("روش پرداخت را انتخاب کنید:", reply_markup=kb)

@router.callback_query(F.data == "pay_card_to_card")
async def pay_card_to_card(call: types.CallbackQuery):
    await call.message.answer("لطفا مبلغ را وارد کنید (تومان):")
    # حالت بعدی باید متن را دریافت و رسید بگیرد - به سادگی نمونه برای ادامه

# ادامه پیاده‌سازی: دریافت مبلغ و رسید و ثبت سفارش (همچنین ارسال رسید به ادمین)

@router.callback_query(F.data == "wallet")
async def wallet_menu(call: types.CallbackQuery):
    balance = get_wallet(call.from_user.id)
    kb = wallet_kb(balance)
    await call.message.edit_text(f"موجودی کیف پول شما: {balance} تومان", reply_markup=kb)

@router.callback_query(F.data == "wallet_topup")
async def wallet_topup_start(call: types.CallbackQuery):
    await call.message.answer("مبلغ افزایش موجودی را به تومان وارد کنید:")

# دریافت مبلغ، ثبت درخواست و ارسال رسید به ادمین در ادامه

@router.callback_query(F.data == "purchase_history")
async def purchase_history(call: types.CallbackQuery):
    purchases = get_purchases(call.from_user.id)
    if not purchases:
        text = "شما تاکنون خریدی نداشته‌اید."
    else:
        text = "سوابق خرید شما:\n"
        for apple_id, price, status in purchases:
            text += f"اپل‌آیدی: {apple_id}\nقیمت: {price}\nوضعیت: {status}\n\n"
    kb = purchase_history_kb()
    await call.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "help")
async def help_text(call: types.CallbackQuery):
    text = (
        "🎯 راهنمای استفاده:\n\n"
        "🔹 خرید سرویس: انتخاب و پرداخت به روش کارت به کارت.\n"
        "🔹 کیف پول: مشاهده موجودی و افزایش آن.\n"
        "🔹 سوابق خرید: نمایش خریدهای قبلی.\n"
        "🔹 در صورت هر سوال به ادمین پیام دهید."
    )
    kb = help_kb()
    await call.message.edit_text(text, reply_markup=kb)
