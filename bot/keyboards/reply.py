# bot/keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/stats")
    button2 = KeyboardButton("/addproduct")
    keyboard.add(button1, button2)
    return keyboard