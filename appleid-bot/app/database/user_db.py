import aiosqlite
from .models import DB_PATH

async def register_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (id, username, full_name)
        VALUES (?, ?, ?)
        """, (user_id, username, full_name))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return await cursor.fetchone()
