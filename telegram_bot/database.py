import sqlite3

# اتصال به دیتابیس
conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
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

    # جدول درخواست‌های افزایش موجودی
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topup_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            request_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # جدول تیکت‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            status TEXT DEFAULT 'open', -- 'open', 'closed'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # جدول اپل آیدی‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apple_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apple_id TEXT,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users(user_id)
        )
    ''')

    # جدول تنظیمات (مثل قوانین، وضعیت سرویس و ...)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # جدول خرید سرویس‌ها توسط کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_name TEXT,
            purchase_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()

# توابع مدیریت دیتابیس

# افزودن کاربر
def add_user(user_id, username, phone_number=None, apple_id=None):
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, phone_number, apple_id) VALUES (?, ?, ?, ?)",
            (user_id, username, phone_number, apple_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در اضافه کردن کاربر: {e}")
        return False

# گرفتن موجودی کیف پول کاربر
def get_user_wallet(user_id):
    cursor.execute("SELECT wallet FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

# به‌روزرسانی موجودی کیف پول
def update_user_wallet(user_id, amount):
    try:
        cursor.execute("UPDATE users SET wallet = wallet + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در به‌روزرسانی کیف پول: {e}")
        return False

# ثبت درخواست افزایش موجودی
def add_topup_request(user_id, amount):
    try:
        cursor.execute(
            "INSERT INTO topup_requests (user_id, amount, status) VALUES (?, ?, 'pending')",
            (user_id, amount)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در ثبت درخواست افزایش موجودی: {e}")
        return False

# دریافت درخواست‌های افزایش موجودی در وضعیت pending
def get_pending_topup_requests():
    cursor.execute("SELECT id, user_id, amount FROM topup_requests WHERE status='pending'")
    return cursor.fetchall()

# تایید یا رد درخواست افزایش موجودی
def set_topup_request_status(req_id, status):
    try:
        cursor.execute("UPDATE topup_requests SET status = ? WHERE id = ?", (status, req_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در تغییر وضعیت درخواست: {e}")
        return False

# مدیریت تیکت‌ها
def create_ticket(user_id, question):
    try:
        cursor.execute(
            "INSERT INTO tickets (user_id, question, status) VALUES (?, ?, 'open')",
            (user_id, question)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در ثبت تیکت: {e}")
        return False

def get_tickets():
    cursor.execute("SELECT ticket_id, user_id, question, status FROM tickets")
    return cursor.fetchall()

def close_ticket(ticket_id):
    try:
        cursor.execute("UPDATE tickets SET status='closed' WHERE ticket_id=?", (ticket_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در بستن تیکت: {e}")
        return False

# مدیریت اپل آیدی‌ها
def add_apple_id(apple_id, owner_id):
    try:
        cursor.execute("INSERT INTO apple_ids (apple_id, owner_id) VALUES (?, ?)", (apple_id, owner_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در افزودن اپل آیدی: {e}")
        return False

def get_apple_ids(owner_id=None):
    if owner_id:
        cursor.execute("SELECT apple_id FROM apple_ids WHERE owner_id=?", (owner_id,))
    else:
        cursor.execute("SELECT apple_id, owner_id FROM apple_ids")
    return cursor.fetchall()

# تنظیمات و قوانین
def set_setting(key, value):
    try:
        cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در تنظیمات: {e}")
        return False

def get_setting(key):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    result = cursor.fetchone()
    return result[0] if result else None

# مدیریت سرویس‌ها
def add_service(name, price):
    try:
        cursor.execute("INSERT INTO services (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در افزودن سرویس: {e}")
        return False

def get_services():
    cursor.execute("SELECT service_id, name, price FROM services")
    return cursor.fetchall()

# ثبت خرید سرویس توسط کاربر
def add_user_service(user_id, service_name, purchase_date):
    try:
        cursor.execute(
            "INSERT INTO user_services (user_id, service_name, purchase_date) VALUES (?, ?, ?)",
            (user_id, service_name, purchase_date)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"خطا در ثبت خرید سرویس: {e}")
        return False

def get_user_services(user_id):
    cursor.execute("SELECT service_name, purchase_date FROM user_services WHERE user_id=?", (user_id,))
    return cursor.fetchall()

# اجرای تابع اولیه برای ساخت جداول (یکبار اجرا کن)
if __name__ == "__main__":
    init_db()