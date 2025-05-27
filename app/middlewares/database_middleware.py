from aiogram.types import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Awaitable, Dict

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict], Awaitable],
        event: TelegramObject,
        data: Dict
    ) -> Awaitable:
        async with self.session_pool() as session:
            data["db_session"] = session
            return await handler(event, data)
