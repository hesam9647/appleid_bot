from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def buy_service_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("پرداخت کارت به کارت", callback_data="pay_card_to_card"),
        InlineKeyboardButton("بازگشت", callback_data="user_main"),
    )
    return kb

def wallet_kb(balance: float):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(f"موجودی: {balance} تومان", callback_data="wallet_balance"),
        InlineKeyboardButton("افزایش موجودی", callback_data="wallet_topup"),
        InlineKeyboardButton("بازگشت", callback_data="user_main"),
    )
    return kb

def purchase_history_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("بازگشت", callback_data="user_main"))
    return kb

def help_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("بازگشت", callback_data="user_main"))
    return kb
