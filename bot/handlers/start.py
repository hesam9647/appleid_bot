from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def register_start_handlers(dp: Dispatcher):
    @dp.message(commands=["start"])
    async def cmd_start(message: types.Message):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("🛒 خرید اپل آیدی"))
        await message.answer("سلام! به ربات فروش اپل آیدی خوش آمدید.", reply_markup=keyboard)
