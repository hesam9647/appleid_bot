from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.flags import get_flag

from app.services.user_service import UserService

class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Get user from event
        user_id = event.from_user.id
        
        # Get required role from handler
        required_role = get_flag(data, "role")
        
        if required_role == "admin":
            config = data['config']
            is_admin = user_id in config.tg_bot.admin_ids
            
            if not is_admin:
                if isinstance(event, CallbackQuery):
                    await event.answer("⛔️ شما دسترسی به این بخش را ندارید!", show_alert=True)
                else:
                    await event.answer("⛔️ شما دسترسی به این بخش را ندارید!")
                return
        
        return await handler(event, data)
