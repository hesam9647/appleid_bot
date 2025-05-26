# database.py
import sqlite3
from config import DB_PATH

### --- Database Initialization --- ###
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # جدول کاربران
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
    ''')

    # جدول اپل آیدی‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS apple_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apple_id TEXT,
            sold INTEGER DEFAULT 0
        )
    ''')

    # جدول سفارشات
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            apple_id TEXT,
            amount REAL,
            status TEXT DEFAULT 'Pending',
            receipt TEXT,
            confirmed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # جدول پرداخت‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            method TEXT,
            amount REAL,
            ref_code TEXT,
            verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # جدول پیام‌های عمومی
    c.execute('''
        CREATE TABLE IF NOT EXISTS broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # جدول وضعیت فروش
    c.execute('''
        CREATE TABLE IF NOT EXISTS service_status (
            id INTEGER PRIMARY KEY,
            is_open INTEGER DEFAULT 1
        )
    ''')
    c.execute('SELECT COUNT(*) FROM service_status')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO service_status (id, is_open) VALUES (1, 1)')

    conn.commit()
    conn.close()


### --- Service Status Functions --- ###
def get_service_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT is_open FROM service_status WHERE id=1')
    status = c.fetchone()[0]
    conn.close()
    return status

def toggle_service_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT is_open FROM service_status WHERE id=1')
    current = c.fetchone()[0]
    new_status = 0 if current == 1 else 1
    c.execute('UPDATE service_status SET is_open=? WHERE id=1', (new_status,))
    conn.commit()
    conn.close()


### --- User Functions --- ###
def add_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def set_user_blocked(user_id, blocked=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET blocked=? WHERE user_id=?', (1 if blocked else 0, user_id))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_balance(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET balance=balance+? WHERE user_id=?', (amount, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE blocked=0')
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]


### --- Apple ID Functions --- ###
def add_apple_id(apple_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO apple_ids (apple_id) VALUES (?)', (apple_id,))
    conn.commit()
    conn.close()

def add_apple_ids_from_excel(ids_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for aid in ids_list:
        c.execute('INSERT INTO apple_ids (apple_id) VALUES (?)', (aid,))
    conn.commit()
    conn.close()

def get_available_apple_id():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT apple_id FROM apple_ids WHERE sold=0 LIMIT 1')
    result = c.fetchone()
    if result:
        apple_id = result[0]
        c.execute('UPDATE apple_ids SET sold=1 WHERE apple_id=?', (apple_id,))
        conn.commit()
        conn.close()
        return apple_id
    conn.close()
    return None

def get_remaining_apple_ids():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM apple_ids WHERE sold=0')
    count = c.fetchone()[0]
    conn.close()
    return count


### --- Order Functions --- ###
def add_order(user_id, apple_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO orders (user_id, apple_id, amount) VALUES (?, ?, ?)', (user_id, apple_id, amount))
    conn.commit()
    conn.close()

def get_user_orders(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE user_id=?', (user_id,))
    orders = c.fetchall()
    conn.close()
    return orders

def set_order_status(order_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    conn.commit()
    conn.close()

def set_order_confirmed(order_id, confirmed=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE orders SET confirmed=? WHERE id=?', (1 if confirmed else 0, order_id))
    conn.commit()
    conn.close()

def save_receipt(order_id, receipt_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE orders SET receipt=? WHERE id=?', (receipt_path, order_id))
    conn.commit()
    conn.close()


### --- Payment Functions --- ###
def log_payment(user_id, method, amount, ref_code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO payments (user_id, method, amount, ref_code)
        VALUES (?, ?, ?, ?)
    ''', (user_id, method, amount, ref_code))
    conn.commit()
    conn.close()

def verify_payment(payment_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE payments SET verified=1 WHERE id=?', (payment_id,))
    conn.commit()
    conn.close()


### --- Broadcast Log --- ###
def save_broadcast(message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO broadcasts (message) VALUES (?)', (message,))
    conn.commit()
    conn.close()
