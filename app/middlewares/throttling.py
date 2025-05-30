from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0):
        self.limit = limit
        self.users_time: Dict[int, float] = {}

    async def __call__(self, handler: Callable, event: Message, data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        last_time = self.users_time.get(user_id, 0)

        if current_time - last_time < self.limit:
            # نادیده گرفتن پیام‌های تکراری خیلی سریع
            return

        self.users_time[user_id] = current_time
        return await handler(event, data)
