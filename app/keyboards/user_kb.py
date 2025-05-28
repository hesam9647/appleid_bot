from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from typing import List
from app.database import Product
def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 خرید سرویس", callback_data="buy_service")
    builder.button(text="💬 تیکت و پشتیبانی", callback_data="support")
    builder.button(text="📚 راهنما", callback_data="help")
    builder.button(text="🧾 سوابق خرید", callback_data="purchase_history")
    builder.button(text="💰 کیف پول", callback_data="wallet")
    builder.button(text="👤 پروفایل", callback_data="profile")
    builder.adjust(2)
    return builder.as_markup()

def wallet_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 افزایش موجودی", callback_data="deposit")
    builder.button(text="📋 تاریخچه تراکنش‌ها", callback_data="transactions")
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 افزایش موجودی", callback_data="deposit")
    builder.button(text="📋 تاریخچه تراکنش‌ها", callback_data="transactions")
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

# اضافه کردن کیبوردهای جدید
def order_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأیید و پرداخت", callback_data="confirm_order")
    builder.button(text="❌ انصراف", callback_data="cancel_order")
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def product_kb(products: List[Product], extra_keyboard: InlineKeyboardBuilder = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Add product buttons
    for product in products:
        if product.stock > 0:
            builder.button(
                text=f"{product.name} - {product.price:,} تومان",
                callback_data=f"product_{product.id}"
            )
    
    # Add extra buttons if provided
    if extra_keyboard:
        for button in extra_keyboard.buttons:
            builder.button(**button)
    else:
        builder.button(text="🔙 بازگشت", callback_data="main_menu")
    
    builder.adjust(1)
    return builder.as_markup()


def product_quantity_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in [1, 2, 3, 5, 10]:
        builder.button(text=str(i), callback_data=f"quantity_{i}")
    builder.button(text="🔙 بازگشت", callback_data="products")
    builder.adjust(5, 1)
    return builder.as_markup()

def order_status_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 پرداخت", callback_data=f"pay_order_{order_id}")
    builder.button(text="❌ لغو سفارش", callback_data=f"cancel_order_{order_id}")
    builder.button(text="🔙 بازگشت", callback_data="orders")
    builder.adjust(2, 1)
    return builder.as_markup()

def orders_list_kb(page: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ قبلی", callback_data=f"orders_page_{page-1}")
    builder.button(text=f"📄 {page}", callback_data="current_page")
    builder.button(text="▶️ بعدی", callback_data=f"orders_page_{page+1}")
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(3, 1)
    return builder.as_markup()


def support_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 تیکت جدید", callback_data="new_ticket")
    builder.button(text="📋 تیکت‌های من", callback_data="my_tickets")
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def purchase_history_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 بازگشت", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def payment_kb(amount: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if amount:
        builder.button(text=f"💳 پرداخت {amount:,} تومان", callback_data=f"pay_{amount}")
    else:
        builder.button(text="💳 50,000 تومان", callback_data="pay_50000")
        builder.button(text="💳 100,000 تومان", callback_data="pay_100000")
        builder.button(text="💳 200,000 تومان", callback_data="pay_200000")
    builder.button(text="🔙 بازگشت", callback_data="wallet")
    builder.adjust(2)
    return builder.as_markup()
