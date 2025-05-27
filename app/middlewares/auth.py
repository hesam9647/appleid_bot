from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.services.user_service import UserService

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Get user
        user_service = UserService(data['session'])
        user = await user_service.get_user(event.from_user.id)
        
        # Check if user is blocked
        if user and user.is_blocked:
            if isinstance(event, CallbackQuery):
                await event.answer("❌ حساب کاربری شما مسدود شده است.", show_alert=True)
            else:
                await event.answer("❌ حساب کاربری شما مسدود شده است.")
            return
        
        # Create user if not exists
        if not user:
            user = await user_service.create_user(
                user_id=event.from_user.id,
                username=event.from_user.username
            )
        
        # Add user to data
        data['user'] = user
        
        return await handler(event, data)
