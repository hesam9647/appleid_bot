import sqlite3
import re

conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

# ساخت جداول مورد نیاز (با بهبودها)
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            wallet REAL DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            phone_number TEXT,  -- اضافه کردن فیلد شماره تلفن
            apple_id TEXT  -- اضافه کردن فیلد اپل ایدی
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()  # مهم: commit بعد از هر عملیات پایگاه داده

# ... (بقیه کدهایتان)

# مثال استفاده از تابع init_db():
# init_db()


# توابع اضافه برای کار با پایگاه داده
def add_user(user_id, username, phone_number=None, apple_id=None):
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, phone_number, apple_id) VALUES (?, ?, ?, ?)", (user_id, username, phone_number, apple_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در اضافه کردن کاربر: {e}")
        return False

def get_user_wallet(user_id):
    cursor.execute("SELECT wallet FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0 # اگر کاربر یافت نشد، 0 برمیگرداند

# ... (بقیه کدهایتان)
