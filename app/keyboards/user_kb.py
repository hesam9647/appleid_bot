from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.database import cursor

# کیبورد اصلی کاربر
def user_main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("خرید سرویس", callback_data="buy_service"),
        InlineKeyboardButton("کیف پول", callback_data="wallet"),
    )
    kb.add(
        InlineKeyboardButton("سوابق خرید", callback_data="purchase_history"),
        InlineKeyboardButton("راهنما", callback_data="help"),
    )
    return kb

# کیبورد خرید سرویس
def buy_service_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("پرداخت کارت به کارت", callback_data="pay_card_to_card"),
        # در آینده می‌توانید درگاه‌های پرداخت دیگر هم اضافه کنید
        InlineKeyboardButton("بازگشت", callback_data="user_main"),
    )
    return kb

# کیبورد کیف پول کاربر
def wallet_kb(balance: float):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(f"💰 موجودی: {balance:,.0f} تومان", callback_data="wallet_balance"),
        InlineKeyboardButton("➕ افزایش موجودی", callback_data="wallet_topup"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="user_main"),
    )
    return kb

# کیبورد سوابق خرید
def purchase_history_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔙 بازگشت", callback_data="user_main")
    )
    return kb

# کیبورد راهنما
def help_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔙 بازگشت", callback_data="user_main")
    )
    return kb

# کیبورد نمایش اپل‌آیدی‌های موجود برای خرید
def available_apple_ids_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    cursor.execute("SELECT id, apple_id, price, location FROM apple_ids WHERE sold=0")
    rows = cursor.fetchall()
    if not rows:
        return None  # یا می‌توانید یک کیبورد فقط با دکمه بازگشت برگردانید

    for id_, apple_id, price, location in rows:
        text = f"{apple_id} | قیمت: {price:,} تومان | مکان: {location}"
        kb.insert(InlineKeyboardButton(text=text, callback_data=f"buy_apple_{id_}"))
    
    kb.add(InlineKeyboardButton("بازگشت", callback_data="user_main"))
    return kb
