from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.config import Config

class AdminAccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        config: Config = data['config']
        
        user_id = event.from_user.id
        if user_id not in config.tg_bot.admin_ids:
            if isinstance(event, CallbackQuery):
                await event.answer("شما دسترسی به این بخش را ندارید!", show_alert=True)
            else:
                await event.answer("شما دسترسی به این بخش را ندارید!")
            return
        
        return await handler(event, data)
