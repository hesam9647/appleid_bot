# utils/cache.py
from aiocache import Cache

cache = Cache(Cache.REDIS, endpoint='127.0.0.1', port=6379)

async def get_cached_data(key):
    return await cache.get(key)

async def set_cached_data(key, value, ttl=300):
    await cache.set(key, value, ttl=ttl)

# نمونه استفاده
# import asyncio
# from utils.cache import get_cached_data, set_cached_data
#
# async def main():
#     await set_cached_data('test_key', 'test_value')
#     value = await get_cached_data('test_key')
#     print(value)
# asyncio.run(main())