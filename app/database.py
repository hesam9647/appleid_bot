import sqlite3
from contextlib import closing

conn = sqlite3.connect("app/data/database.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        wallet_balance REAL DEFAULT 0,
        blocked INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apple_ids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apple_id TEXT,
        sold INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        apple_id TEXT,
        price REAL,
        status TEXT DEFAULT 'pending',  -- pending, approved, rejected
        payment_method TEXT,
        payment_proof TEXT,  -- عکس رسید یا متن
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()

def add_user(user_id: int, username: str):
    with closing(conn.cursor()) as c:
        c.execute("INSERT OR IGNORE INTO users(user_id, username) VALUES (?,?)", (user_id, username))
        conn.commit()

def block_user(user_id: int, block: bool):
    with closing(conn.cursor()) as c:
        c.execute("UPDATE users SET blocked=? WHERE user_id=?", (1 if block else 0, user_id))
        conn.commit()

def is_user_blocked(user_id: int):
    with closing(conn.cursor()) as c:
        c.execute("SELECT blocked FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return row and row[0] == 1

def update_wallet(user_id: int, amount: float):
    with closing(conn.cursor()) as c:
        c.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id=?", (amount, user_id))
        conn.commit()

def get_wallet(user_id: int):
    with closing(conn.cursor()) as c:
        c.execute("SELECT wallet_balance FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return row[0] if row else 0.0

def add_apple_id(apple_id: str):
    with closing(conn.cursor()) as c:
        c.execute("INSERT INTO apple_ids (apple_id) VALUES (?)", (apple_id,))
        conn.commit()

def get_available_apple_id():
    with closing(conn.cursor()) as c:
        c.execute("SELECT id, apple_id FROM apple_ids WHERE sold=0 LIMIT 1")
        return c.fetchone()

def mark_apple_id_sold(id_):
    with closing(conn.cursor()) as c:
        c.execute("UPDATE apple_ids SET sold=1 WHERE id=?", (id_,))
        conn.commit()

def add_purchase(user_id: int, apple_id: str, price: float, payment_method: str, payment_proof: str = None):
    with closing(conn.cursor()) as c:
        c.execute("INSERT INTO purchases (user_id, apple_id, price, payment_method, payment_proof) VALUES (?,?,?,?,?)",
                  (user_id, apple_id, price, payment_method, payment_proof))
        conn.commit()
        return c.lastrowid

def get_purchases(user_id: int):
    with closing(conn.cursor()) as c:
        c.execute("SELECT apple_id, price, status FROM purchases WHERE user_id=? ORDER BY id DESC", (user_id,))
        return c.fetchall()

def get_all_users():
    with closing(conn.cursor()) as c:
        c.execute("SELECT user_id FROM users")
        return [row[0] for row in c.fetchall()]

def get_all_users_info():
    with closing(conn.cursor()) as c:
        c.execute("SELECT user_id, username, wallet_balance, blocked FROM users")
        return c.fetchall()

def get_purchase_by_id(purchase_id: int):
    with closing(conn.cursor()) as c:
        c.execute("SELECT * FROM purchases WHERE id=?", (purchase_id,))
        return c.fetchone()

def update_purchase_status(purchase_id: int, status: str):
    with closing(conn.cursor()) as c:
        c.execute("UPDATE purchases SET status=? WHERE id=?", (status, purchase_id))
        conn.commit()

def set_setting(key: str, value: str):
    with closing(conn.cursor()) as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
        conn.commit()

def get_setting(key: str):
    with closing(conn.cursor()) as c:
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        return row[0] if row else None

def get_all_apple_ids():
    with closing(conn.cursor()) as c:
        c.execute("SELECT id, apple_id, sold FROM apple_ids")
        return c.fetchall()
