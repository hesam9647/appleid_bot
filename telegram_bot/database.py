import sqlite3

# اتصال به دیتابیس SQLite
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

# تابع ایجاد جداول دیتابیس
def init_db():
    try:
        # جدول کاربران
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

        # جدول سرویس‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                price REAL
            )
        ''')

        # جدول تیکت‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("دیتابیس با موفقیت ایجاد شد.")
    except sqlite3.Error as e:
        print(f"خطا در ایجاد دیتابیس: {e}")

# تابع افزودن کاربر اگر وجود نداشت
def add_user_if_not_exists(user_id, username):
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
            conn.commit()
    except sqlite3.Error as e:
        print(f"خطا در افزودن کاربر: {e}")
