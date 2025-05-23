import sqlite3

# اتصال به دیتابیس
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    """
    ساختار دیتابیس را ایجاد می کند.
    """
    try:
        # ساخت جدول کاربران
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

        # ساخت جدول سرویس‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL
            )
        ''')

        # ساخت جدول درخواست‌های افزایش موجودی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposit_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول خریدهای کاربران (با ستون amount)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_id INTEGER,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("دیتابیس با موفقیت ایجاد شد.")
    except sqlite3.Error as e:
        print(f"خطا در ایجاد دیتابیس: {e}")


def add_service(name, price):
    """
    یک سرویس جدید به دیتابیس اضافه می کند.
    """
    try:
        cursor.execute("INSERT INTO services (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        print(f"سرویس {name} با موفقیت اضافه شد.")
    except sqlite3.Error as e:
        print(f"خطا در اضافه کردن سرویس: {e}")


def get_all_services():
    """
    لیست تمام سرویس ها را برمی گرداند.
    """
    try:
        cursor.execute("SELECT * FROM services")
        services = cursor.fetchall()
        return services
    except sqlite3.Error as e:
        print(f"خطا در دریافت سرویس ها: {e}")
        return None


def add_user_if_not_exists(user_id, username):
    """
    اگر کاربر وجود نداشته باشد، آن را اضافه می‌کند.
    """
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
            conn.commit()
            print(f"کاربر {username} اضافه شد.")
    except sqlite3.Error as e:
        print(f"خطا در افزودن کاربر: {e}")


# اجرای اولیه
if __name__ == "__main__":
    init_db()

    # مثال: اضافه کردن سرویس‌ها
    add_service("سرویس 1", 10.00)
    add_service("سرویس 2", 20.00)

    # مثال: چاپ سرویس‌ها
    services = get_all_services()
    if services:
        for service in services:
            print(service)
