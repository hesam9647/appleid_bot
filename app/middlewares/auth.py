from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class AuthMiddleware(BaseMiddleware):
    def __init__(self, config):
        self.config = config
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Add config to data
        data['config'] = self.config
        
        return await handler(event, data)
