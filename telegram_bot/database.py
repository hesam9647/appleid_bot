import sqlite3

# اتصال به دیتابیس
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    """
    ساختار دیتابیس را ایجاد می‌کند.
    """
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
                name TEXT,
                price REAL
            )
        ''')

        # جدول درخواست‌های افزایش موجودی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposit_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول خریدهای کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_id INTEGER,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول اپل آیدی‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apple_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apple_id TEXT,
                owner_id TEXT
            )
        ''')

        # جدول تیکت‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول درخواست‌های topup
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topup_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("دیتابیس با موفقیت ایجاد شد.")
    except sqlite3.Error as e:
        print(f"خطا در ایجاد دیتابیس: {e}")

# اجرای تابع برای ساخت جداول
if __name__ == "__main__":
    init_db()
