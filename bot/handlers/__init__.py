from aiogram import Router, Dispatcher
from . import start

def register_all_handlers(dp: Dispatcher, config):
    dp.include_router(start.router)
