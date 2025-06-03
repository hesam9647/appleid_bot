import aiosqlite
from .models import DB_PATH

async def add_balance(user_id: int, amount: int, description: str = "افزایش موجودی"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET wallet = wallet + ? WHERE id = ?", (amount, user_id))
        await db.execute("""
            INSERT INTO transactions (user_id, amount, type, description)
            VALUES (?, ?, ?, ?)
        """, (user_id, amount, "increase", description))
        await db.commit()

async def get_balance(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT wallet FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0
