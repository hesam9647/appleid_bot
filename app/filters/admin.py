from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union

class AdminFilter(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        config = event.bot.config  # ✅ درست
        return event.from_user.id in config.tg_bot.admin_ids
