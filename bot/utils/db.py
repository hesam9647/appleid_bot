import sqlalchemy
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from bot.config import load_config
config = load_config()
ADMINS = config.admins

Base = declarative_base()  # ایجاد کلاس پایه برای مدل‌ها

async def create_db(database_url):
    # ساخت ارتباط با دیتابیس به صورت غیر همزمان
    engine = create_async_engine(database_url, echo=True)

    # ساخت جلسه به صورت غیر همزمان
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # ایجاد جداول برای تمامی مدل‌ها
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # اتصال به دیتابیس و انجام عملیات در صورت نیاز
    async with async_session() as session:
        async with session.begin():
            pass  # می‌توانید عملیات دیتابیس خود را در اینجا انجام دهید

    print("✅ دیتابیس به درستی ایجاد شد.")

def create_stats_table():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    users_count INTEGER,
                    sales_count INTEGER,
                    transactions_count INTEGER
                )''')
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM stats ORDER BY id DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result if result else (0, 0, 0)

def create_products_table():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price REAL
                )''')
    conn.commit()
    conn.close()

def add_product(name, price):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()
    return products


def block_user(user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO blocked_users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def unblock_user(user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('DELETE FROM blocked_users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_blocked_users():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT user_id FROM blocked_users')
    users = c.fetchall()
    conn.close()
    return [user[0] for user in users]
