from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.utils import db

router = Router()

# --- کیبورد استارت ---
@router.message(F.text == "/start")
async def start_cmd(message: types.Message):
    db.add_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 خرید اپل آیدی")],
            [KeyboardButton(text="👜 کیف پول من"), KeyboardButton(text="🛍 سفارش‌های من")],
            [KeyboardButton(text="🎫 تیکت و پشتیبانی")]
        ],
        resize_keyboard=True
    )
    await message.answer("سلام! به پنل کاربری خوش آمدید.", reply_markup=markup)

# --- کیف پول من ---
@router.message(F.text == "👜 کیف پول من")
async def wallet(message: types.Message):
    balance = db.get_wallet(message.from_user.id)
    await message.answer(f"موجودی کیف پول شما: {balance} تومان")

# --- سفارش‌های من ---
@router.message(F.text == "🛍 سفارش‌های من")
async def orders(message: types.Message):
    user_id = message.from_user.id
    orders = db.get_orders(user_id)
    if not orders:
        await message.answer("❗ شما هنوز سفارشی ثبت نکرده‌اید.")
        return

    text = "🛍 سفارش‌های شما:\n\n"
    for i, (product, date) in enumerate(orders, start=1):
        text += f"{i}. {product}\n📅 {date}\n\n"

    await message.answer(text)

# --- ارسال تیکت ---
class Support(StatesGroup):
    writing = State()

@router.message(F.text == "🎫 تیکت و پشتیبانی")
async def support(message: types.Message, state: FSMContext):
    await message.answer("📝 لطفاً پیام خود را بنویسید:")
    await state.set_state(Support.writing)

@router.message(Support.writing)
async def receive_ticket(message: types.Message, state: FSMContext):
    db.add_ticket(user_id=message.from_user.id, message=message.text)
    await message.answer("✅ تیکت شما با موفقیت ثبت شد. پشتیبانی به زودی پاسخ خواهد داد.")
    await state.clear()

# --- خرید اپل آیدی ---
class BuyProduct(StatesGroup):
    choosing = State()

@router.message(F.text == "🛒 خرید اپل آیدی")
async def start_buy(message: types.Message, state: FSMContext):
    await message.answer("لطفاً نوع اپل آیدی مورد نظر را وارد کنید (مثلاً: آمریکا - دائمی - اختصاصی):")
    await state.set_state(BuyProduct.choosing)

@router.message(BuyProduct.choosing)
async def process_buy(message: types.Message, state: FSMContext):
    product = message.text
    user_id = message.from_user.id
    current_balance = db.get_wallet(user_id)

    price = 50000  # قیمت ثابت برای تست

    if current_balance < price:
        await message.answer("❌ موجودی کیف پول کافی نیست. لطفاً ابتدا آن را شارژ کنید.")
    else:
        db.update_wallet(user_id, -price)
        db.add_order(user_id, product)
        await message.answer(f"✅ سفارش شما برای «{product}» ثبت شد.\n💳 مبلغ {price} تومان از کیف پول شما کسر شد.")
    await state.clear()
