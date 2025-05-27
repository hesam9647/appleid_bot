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

def payment_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 50,000 تومان", callback_data="pay_50000")
    builder.button(text="💳 100,000 تومان", callback_data="pay_100000")
    builder.button(text="💳 200,000 تومان", callback_data="pay_200000")
    builder.button(text="🔙 بازگشت", callback_data="wallet")
    builder.adjust(2)
    return builder.as_markup()

def product_kb(products: List[Product]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for product in products:
        if product.stock > 0:
            builder.button(
                text=f"{product.name} - {product.base_price:,} تومان",
                callback_data=f"product_{product.id}"
            )
    
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def order_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأیید و پرداخت", callback_data="confirm_order")
    builder.button(text="❌ انصراف", callback_data="cancel_order")
    builder.adjust(1)
    return builder.as_markup()

def payment_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 پرداخت", callback_data=f"pay_order_{order_id}")
    builder.button(text="❌ انصراف", callback_data=f"cancel_order_{order_id}")
    builder.adjust(1)
    return builder.as_markup()
