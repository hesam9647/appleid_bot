from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="manage_users")],
            [InlineKeyboardButton(text="💳 مدیریت تراکنش‌ها", callback_data="manage_transactions")],
        ]
    )

def user_manage_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 افزودن اعتبار", callback_data=f"add_credit:{user_id}")],
        ]
    )
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def support_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 پشتیبانی", callback_data="support")],
        ]
    )

def ticket_list_keyboard(tickets: list):
    buttons = [
        [InlineKeyboardButton(text=f"📨 #{ticket[0]} از {ticket[1]}", callback_data=f"ticket:{ticket[0]}")]
        for ticket in tickets
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
