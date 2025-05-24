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
                apple_id TEXT,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        # جدول اتصال کاربر به سرویس
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_id INTEGER,
                purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        # جدول اپل آیدی‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apple_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apple_id TEXT UNIQUE,
                owner_id TEXT,
                sold INTEGER DEFAULT 0
            )
        ''')

        # جدول درخواست‌های افزایش موجودی (topup_requests)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topup_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                status TEXT -- مثلا: 'pending', 'approved', 'rejected'
            )
        ''')

        # جدول تنظیمات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        conn.commit()
        print("دیتابیس با موفقیت ایجاد شد.")
    except sqlite3.Error as e:
        print(f"خطا در ایجاد دیتابیس: {e}")

# تابع افزودن کاربر در صورت عدم وجود
def add_user_if_not_exists(user_id, username):
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
            conn.commit()
            print(f"کاربر با شناسه {user_id} اضافه شد.")
    except sqlite3.Error as e:
        print(f"خطا در افزودن کاربر: {e}")

# در صورت نیاز، می‌توانید تابع را صدا بزنید تا جداول ساخته شوند
# init_db()