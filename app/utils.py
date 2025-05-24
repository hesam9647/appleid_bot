import asyncio
from aiogram import Bot
from config import ADMIN_IDS

async def broadcast_message(bot: Bot, text: str):
    users = await get_all_users()
    for user_id in users:
        try:
            await bot.send_message(user_id, text)
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

# کار با فایل اکسل با pandas
import pandas as pd
from database import add_apple_id

def excel_to_apple_ids(file_path):
    df = pd.read_excel(file_path)
    # فرض می‌کنیم ستون اول اپل آیدی‌ها باشد
    for apple_id in df.iloc[:,0]:
        if isinstance(apple_id, str):
            add_apple_id(apple_id.strip())
