from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.config import Config


class AdminAccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        config: Config = data.get("config")

        if not config:
            # اگر کانفیگ وجود ندارد، عبور نکن
            if isinstance(event, Message):
                await event.answer("⚠️ پیکربندی ربات پیدا نشد.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ پیکربندی ربات پیدا نشد.", show_alert=True)
            return

        user_id = event.from_user.id

        if user_id not in config.tg_bot.admin_ids:
            if isinstance(event, CallbackQuery):
                await event.answer("⛔ شما دسترسی به این بخش را ندارید!", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("⛔ شما دسترسی به این بخش را ندارید!")
            return

        return await handler(event, data)
class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        print(f"⚙️ Event received: {event}")
        return await handler(event, data)
