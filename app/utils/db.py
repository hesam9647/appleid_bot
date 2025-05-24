# utils/db.py
import asyncpg

async def create_connection():
    conn = await asyncpg.connect(
        user='your_user',
        password='your_password',
        database='your_db',
        host='localhost'
    )
    return conn

# نمونه استفاده در فایل‌های دیگر
# import asyncio
# from utils.db import create_connection
#
# async def main():
#     conn = await create_connection()
#     # عملیات
#     await conn.close()
#
# asyncio.run(main())