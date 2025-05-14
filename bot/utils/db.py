import sqlite3

def create_db(database_url):
    # اتصال به دیتابیس SQLite (در اینجا از sqlite3 استفاده شده)
    conn = sqlite3.connect(database_url.split('///')[-1])  # دریافت نام فایل دیتابیس از URL
    cursor = conn.cursor()

    # ایجاد جداول دیتابیس (مثال: یک جدول ساده برای کاربران)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        user_id INTEGER UNIQUE NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ دیتابیس با موفقیت ایجاد شد.")
