from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import json
import hashlib
from datetime import datetime, timedelta

class CacheMiddleware(BaseMiddleware):
    def __init__(self, redis_client, expire_time: int = 300):
        self.redis = redis_client
        self.expire_time = expire_time

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Skip caching for admin requests
        if event.from_user.id in data['config'].tg_bot.admin_ids:
            return await handler(event, data)
            
        # Generate cache key
        if isinstance(event, Message):
            cache_key = f"cache:{event.from_user.id}:{event.text}"
        else:
            cache_key = f"cache:{event.from_user.id}:{event.data}"
            
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Try to get from cache
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
            
        # Process request
        response = await handler(event, data)
        
        # Save to cache
        if response:
            await self.redis.set(
                cache_key,
                json.dumps(response),
                ex=self.expire_time
            )
            
        return response
