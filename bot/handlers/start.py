# bot/handlers/start.py

from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("سلام! به ربات خوش اومدی 🌟")
