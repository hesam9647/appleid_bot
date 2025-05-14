from aiogram import Dispatcher
from bot.handlers import start, admin, user

def register_routers(dp: Dispatcher):
    admin.register_router(dp)  # این تغییر به register_router برای admin
    dp.include_router(start.router)
    dp.include_router(user.router)
