# reports.py
import sqlite3  # یا دیتابیس مورد استفاده‌ت

def fetch_sales_report():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total_sales, SUM(amount) AS total_amount FROM orders WHERE status='Completed'")
    result = cursor.fetchone()
    conn.close()
    return {
        'total_sales': result[0],
        'total_amount': result[1]
    }