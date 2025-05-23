import sqlite3

# اتصال به دیتابیس (گلوبال نگه دار)
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                wallet REAL DEFAULT 0,
                is_blocked INTEGER DEFAULT 0,
                phone_number TEXT,
                apple_id TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                price REAL
            )
        ''')
        conn.commit()
        print("دیتابیس با موفقیت ایجاد شد.")
    except sqlite3.Error as e:
        print(f"خطا در ایجاد دیتابیس: {e}")

def add_user_if_not_exists(user_id, username=None, phone_number=None, apple_id=None):
    try:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user is None:
            cursor.execute(
                "INSERT INTO users (user_id, username, phone_number, apple_id) VALUES (?, ?, ?, ?)",
                (user_id, username, phone_number, apple_id)
            )
            conn.commit()
            return True
        return False
    except sqlite3.Error as e:
        print(f"خطا در اضافه کردن کاربر: {e}")
        return False
