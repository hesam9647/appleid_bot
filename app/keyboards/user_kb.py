from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 خرید سرویس", callback_data="buy_service")
    builder.button(text="💬 تیکت و پشتیبانی", callback_data="support")
    builder.button(text="📚 راهنما", callback_data="help")
    builder.button(text="🧾 سوابق خرید", callback_data="purchase_history")
    builder.button(text="💰 کیف پول", callback_data="wallet")
    builder.button(text="🎁 کد هدیه", callback_data="gift_code")
    builder.button(text="📊 تعرفه‌ها", callback_data="prices")
    builder.adjust(2)
    return builder.as_markup()

def wallet_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 افزایش موجودی", callback_data="deposit")
    builder.button(text="📋 تاریخچه تراکنش‌ها", callback_data="transactions")
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()
