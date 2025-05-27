from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union

class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user.id in self.admin_ids

class IsOwner(BaseFilter):
    def __init__(self, owner_id: int) -> None:
        self.owner_id = owner_id

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        return event.from_user.id == self.owner_id
