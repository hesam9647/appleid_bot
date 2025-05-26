from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.user_kb import (
    user_main_kb, buy_service_kb, wallet_kb, purchase_history_kb, help_kb, available_apple_ids_kb
)
from app.utils.database import (
    get_wallet, get_purchases, add_ticket,
    mark_apple_id_sold, add_purchase,
    cursor, conn
)

router = Router()

# وضعیت‌ها برای تیکت و پرداخت
class TicketStates(StatesGroup):
    waiting_for_ticket_message = State()

class PaymentStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_receipt = State()

# مپ موقت برای ذخیره‌ی خرید کاربر
user_data = {}

# منوی اصلی کاربر
@router.callback_query(F.data == "user_main")
async def user_main_menu(call: types.CallbackQuery):
    kb = user_main_kb()
    await call.message.edit_text("پنل کاربری شما:", reply_markup=kb)

# منوی خرید سرویس
@router.callback_query(F.data == "buy_service")
async def buy_service_menu(call: types.CallbackQuery):
    kb = buy_service_kb()
    await call.message.edit_text("روش پرداخت را انتخاب کنید:", reply_markup=kb)

# نمایش موجودی کیف پول
@router.callback_query(F.data == "wallet")
async def wallet_menu(call: types.CallbackQuery):
    balance = get_wallet(call.from_user.id)
    kb = wallet_kb(balance)
    await call.message.edit_text(f"موجودی کیف پول شما: {balance} تومان", reply_markup=kb)

# شروع فرآیند افزایش موجودی
@router.callback_query(F.data == "wallet_topup")
async def wallet_topup_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("مبلغ افزایش موجودی را به تومان وارد کنید:")
    await state.set_state(PaymentStates.waiting_for_amount)

# دریافت مبلغ افزایش موجودی
@router.message(PaymentStates.waiting_for_amount, F.text)
async def receive_topup_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("لطفا فقط عدد وارد کنید.")
        return

    amount = int(message.text)
    if amount <= 0:
        await message.reply("مبلغ باید بیشتر از صفر باشد.")
        return

    await state.update_data(amount=amount)
    await message.answer("لطفا رسید پرداخت کارت به کارت را ارسال کنید:")
    await state.set_state(PaymentStates.waiting_for_receipt)

# دریافت رسید کارت به کارت
@router.message(PaymentStates.waiting_for_receipt, content_types=types.ContentType.DOCUMENT)
async def receive_topup_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")

    # TODO: ارسال رسید به ادمین یا ذخیره در DB
    await message.answer(f"رسید افزایش موجودی به مبلغ {amount} تومان دریافت شد. پس از تایید، موجودی شما افزایش می‌یابد.")
    await state.clear()

# نمایش تاریخچه خریدها
@router.callback_query(F.data == "purchase_history")
async def purchase_history(call: types.CallbackQuery):
    purchases = get_purchases(call.from_user.id)
    if not purchases:
        text = "شما تاکنون خریدی نداشته‌اید."
    else:
        text = "سوابق خرید شما:\n"
        for apple_id, price, status in purchases:
            text += f"اپل‌آیدی: {apple_id}\nقیمت: {price} تومان\nوضعیت: {status}\n\n"
    kb = purchase_history_kb()
    await call.message.edit_text(text, reply_markup=kb)

# نمایش راهنما
@router.callback_query(F.data == "help")
async def help_text(call: types.CallbackQuery):
    text = (
        "🎯 راهنمای استفاده:\n\n"
        "🔹 خرید اپل‌آیدی: انتخاب اپل‌آیدی و پرداخت کارت‌به‌کارت یا آنلاین.\n"
        "🔹 کیف پول: مشاهده موجودی و افزایش آن.\n"
        "🔹 سوابق خرید: مشاهده سفارش‌های قبلی.\n"
        "🔹 در صورت سوال با پشتیبانی تماس بگیرید."
    )
    kb = help_kb()
    await call.message.edit_text(text, reply_markup=kb)

# ارسال تیکت پشتیبانی
@router.callback_query(F.data == "support_ticket")
async def ask_ticket_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("لطفاً پیام خود را برای پشتیبانی بنویسید:")
    await state.set_state(TicketStates.waiting_for_ticket_message)

@router.message(TicketStates.waiting_for_ticket_message)
async def receive_ticket_message(message: types.Message, state: FSMContext):
    add_ticket(message.from_user.id, message.text)
    await message.answer("✅ تیکت شما ثبت شد. منتظر پاسخ بمانید.")
    await state.clear()

# شروع خرید اپل‌آیدی
@router.message(commands=["buy_apple_id"])
async def start_buy_apple_id(message: types.Message):
    kb = available_apple_ids_kb()
    if kb.inline_keyboard:
        await message.reply("لطفا اپل‌آیدی مورد نظر خود را انتخاب کنید:", reply_markup=kb)
    else:
        await message.reply("در حال حاضر اپل‌آیدی فروشی موجود نیست.")

# انتخاب اپل‌آیدی
@router.callback_query(F.data.startswith("buy_apple_"))
async def process_apple_id_choice(callback_query: types.CallbackQuery):
    apple_id_db_id = int(callback_query.data.split("_")[-1])
    cursor.execute("SELECT apple_id, price FROM apple_ids WHERE id = ? AND sold = 0", (apple_id_db_id,))
    row = cursor.fetchone()

    if not row:
        await callback_query.answer("این اپل‌آیدی قبلاً فروخته شده یا موجود نیست.", show_alert=True)
        return

    apple_id, price = row
    user_data[callback_query.from_user.id] = {
        'apple_id_id': apple_id_db_id,
        'apple_id': apple_id,
        'price': price
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💳 کارت به کارت", callback_data="payment_card")],
        [InlineKeyboardButton("🌐 درگاه آنلاین", callback_data="payment_online")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_payment")]
    ])

    await callback_query.message.edit_text(
        f"شما اپل‌آیدی {apple_id} با قیمت {price} تومان را انتخاب کردید.\nلطفا روش پرداخت را انتخاب کنید:",
        reply_markup=kb
    )

# پرداخت با کارت به کارت
@router.callback_query(F.data == "payment_card")
async def process_card_payment(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        await callback_query.answer("ابتدا باید اپل‌آیدی را انتخاب کنید.", show_alert=True)
        return

    user_data[user_id]['payment_method'] = 'card'
    await callback_query.message.answer("لطفاً رسید کارت به کارت خود را ارسال کنید:")

@router.message(lambda m: user_data.get(m.from_user.id, {}).get('payment_method') == 'card', content_types=types.ContentType.DOCUMENT)
async def receive_card_payment_receipt(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id)
    if not data:
        await message.reply("ابتدا باید اپل‌آیدی را انتخاب کنید.")
        return

    # TODO: اطلاع به ادمین یا ذخیره رسید
    await message.reply("رسید دریافت شد. پس از تایید، اپل‌آیدی برای شما ارسال خواهد شد.")

# لغو پرداخت
@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data.pop(user_id, None)
    await callback_query.message.edit_text("پرداخت لغو شد. برای شروع مجدد /buy_apple_id را ارسال کنید.")

# ثبت تمام هندلرها
def register_user_handlers(dp):
    dp.include_router(router)
