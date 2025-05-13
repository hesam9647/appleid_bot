from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📦 خرید اپل آیدی")],
        [KeyboardButton(text="🧾 پیگیری سفارش")],
        [KeyboardButton(text="📚 آموزش‌ها")],
        [KeyboardButton(text="⚙️ تنظیمات")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
