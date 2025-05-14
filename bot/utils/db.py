import aiosqlite

async def create_db(database_url):
    db_path = database_url.split("///")[-1]
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price INTEGER
            );
        """)
        await db.commit()

async def get_stats():
    async with aiosqlite.connect("db.sqlite3") as db:
        u = await db.execute("SELECT COUNT(*) FROM users")
        s = await db.execute("SELECT SUM(price) FROM products")
        t = await db.execute("SELECT COUNT(*) FROM products")
        users = (await u.fetchone())[0]
        sales = (await s.fetchone())[0] or 0
        txs = (await t.fetchone())[0]
        return users, sales, txs

async def add_product(name, price):
    async with aiosqlite.connect("db.sqlite3") as db:
        await db.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        await db.commit()

async def get_products():
    async with aiosqlite.connect("db.sqlite3") as db:
        cursor = await db.execute("SELECT * FROM products")
        return await cursor.fetchall()

async def block_user(user_id): pass  # می‌تونی جدول بلاک شده‌ها اضافه کنی
async def unblock_user(user_id): pass