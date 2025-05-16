import sqlite3
from datetime import datetime

def connect():
    return sqlite3.connect("db.sqlite3")

def init_db():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            balance INTEGER DEFAULT 0
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product TEXT,
            created_at TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            created_at TEXT
        )
        """)

# ---------------- عملیات روی دیتابیس ----------------

def add_user(user_id: int, full_name: str, username: str):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO users (user_id, full_name, username)
            VALUES (?, ?, ?)
        """, (user_id, full_name, username))

def get_user_balance(user_id: int) -> int:
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
    return result[0] if result else 0

def update_balance(user_id: int, amount: int):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

def add_order(user_id: int, product: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (user_id, product, created_at)
            VALUES (?, ?, ?)
        """, (user_id, product, now))

def get_orders(user_id: int):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT product, created_at FROM orders
            WHERE user_id = ? ORDER BY id DESC
        """, (user_id,))
        return cur.fetchall()

def add_ticket(user_id: int, message: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tickets (user_id, message, created_at)
            VALUES (?, ?, ?)
        """, (user_id, message, now))

def get_tickets(user_id: int):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT message, created_at FROM tickets
            WHERE user_id = ? ORDER BY id DESC
        """, (user_id,))
        return cur.fetchall()

def get_user(user_id: int):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()
