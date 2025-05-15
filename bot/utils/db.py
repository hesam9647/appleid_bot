import sqlite3

def connect():
    return sqlite3.connect("db.sqlite3")

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        wallet INTEGER DEFAULT 0
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

    conn.commit()
    conn.close()


# ---- عملیات روی دیتابیس ----

def add_user(user_id: int, full_name: str, username: str):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, full_name, username) VALUES (?, ?, ?)", (user_id, full_name, username))
    conn.commit()
    conn.close()

def get_wallet(user_id: int) -> int:
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT wallet FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def update_wallet(user_id: int, amount: int):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET wallet = wallet + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_order(user_id: int, product: str):
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, product, created_at) VALUES (?, ?, ?)", (user_id, product, now))
    conn.commit()
    conn.close()

def get_orders(user_id: int):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT product, created_at FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,))
    results = cur.fetchall()
    conn.close()
    return results

def add_ticket(user_id: int, message: str):
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO tickets (user_id, message, created_at) VALUES (?, ?, ?)", (user_id, message, now))
    conn.commit()
    conn.close()

def get_tickets(user_id: int):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT message, created_at FROM tickets WHERE user_id = ? ORDER BY id DESC", (user_id,))
    results = cur.fetchall()
    conn.close()
    return results

def get_user(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


