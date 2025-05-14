from aiogram import Bot, Dispatcher
from aiogram.types import Message
from bot.config import BOT_TOKEN

# ایجاد ربات و دیسپچر
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ثبت روت‌ها و هندلرها
async def register_routers(dp: Dispatcher):
    # اضافه کردن هندلرها به دیسپچر
    pass

# ثبت روت‌ها
register_routers(dp)

async def on_start(message: Message):
    await message.answer("سلام! به ربات خوش آمدید.")

dp.register_message_handler(on_start, commands=["start"])

async def main():
    # شروع پردازش پیام‌ها
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
