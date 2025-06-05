import sqlite3
from typing import Dict, List, Any, Optional
from config.config import DATABASE_PATH
from database.models import *

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        """ایجاد جداول مورد نیاز"""
        self.cursor.execute(CREATE_USERS_TABLE)
        self.cursor.execute(CREATE_APPLE_IDS_TABLE)
        self.cursor.execute(CREATE_TRANSACTIONS_TABLE)
        self.cursor.execute(CREATE_TICKETS_TABLE)

        # جدول پاسخ‌های تیکت
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                admin_id INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول پرداخت‌ها
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                payment_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    # =================== مدیریت کاربران ===================

    def add_user(self, user_id: int, username: str) -> None:
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        self.conn.commit()

    def toggle_user_block(self, user_id: int) -> bool:
        try:
            self.cursor.execute(
                "UPDATE users SET is_blocked = NOT is_blocked WHERE user_id = ?",
                (user_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error toggling user block: {e}")
            return False

    def add_user_note(self, user_id: int, note: str) -> bool:
        try:
            self.cursor.execute(
                "UPDATE users SET note = ? WHERE user_id = ?",
                (note, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user note: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return {
                "user_id": result[0],
                "username": result[1],
                "balance": result[2],
                "is_blocked": result[3],
                "created_at": result[4],
                "note": result[5] if len(result) > 5 else None
            }
        return None

    def get_filtered_users(self, filter_type: str) -> List[Dict]:
        query = "SELECT * FROM users"
        if filter_type == 'blocked':
            query += " WHERE is_blocked = 1"
        elif filter_type == 'buyers':
            query += " WHERE purchases_count > 0"
        self.cursor.execute(query)
        users = self.cursor.fetchall()
        return [{
            'user_id': u[0],
            'username': u[1],
            'balance': u[2],
            'is_blocked': u[3],
            'created_at': u[4],
            'note': u[5] if len(u) > 5 else None
        } for u in users]

    def get_all_users(self) -> List[Dict]:
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        return [{"user_id": user[0], "username": user[1], "balance": user[2]} for user in users]

    def update_balance(self, user_id: int, amount: int) -> bool:
        try:
            self.cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating balance: {e}")
            return False

    # =================== مدیریت اپل آیدی ===================

    def add_apple_id(self, data: dict) -> bool:
        try:
            self.cursor.execute("""
                INSERT INTO apple_ids (email, password, email_password, birth_date, security_questions)
                VALUES (?, ?, ?, ?, ?)
            """, (data['email'], data['password'], data['email_password'], 
                  data['birth_date'], data['security_questions']))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding Apple ID: {e}")
            return False

    def get_apple_ids(self) -> List[Dict]:
        self.cursor.execute("SELECT * FROM apple_ids")
        apple_ids = self.cursor.fetchall()
        return [
            {
                'id': row[0],
                'email': row[1],
                'status': row[11],
                'type': row[12]
            }
            for row in apple_ids
        ]

    # =================== پرداخت ===================

    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        self.cursor.execute(
            "SELECT * FROM payments WHERE payment_id = ?",
            (payment_id,)
        )
        payment = self.cursor.fetchone()
        if payment:
            return {
                'id': payment[0],
                'user_id': payment[1],
                'amount': payment[2],
                'payment_id': payment[3],
                'status': payment[4]
            }
        return None

    def update_payment_status(self, payment_id: str, status: str) -> None:
        self.cursor.execute(
            "UPDATE payments SET status = ? WHERE payment_id = ?",
            (status, payment_id)
        )
        self.conn.commit()

    # =================== تیکت و پاسخ ===================

    def create_ticket(self, user_id: int, title: str, message: str) -> int:
        self.cursor.execute("""
            INSERT INTO tickets (user_id, title, message, status)
            VALUES (?, ?, ?, 'open')
        """, (user_id, title, message))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user_tickets(self, user_id: int) -> List[Dict]:
        self.cursor.execute("""
            SELECT id, title, status, created_at
            FROM tickets
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        tickets = self.cursor.fetchall()
        return [{
            'id': t[0],
            'title': t[1],
            'status': t[2],
            'created_at': t[3]
        } for t in tickets]

    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        self.cursor.execute("""
            SELECT t.*, u.username
            FROM tickets t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.id = ?
        """, (ticket_id,))
        t = self.cursor.fetchone()
        if t:
            return {
                'id': t[0],
                'user_id': t[1],
                'title': t[2],
                'message': t[3],
                'status': t[4],
                'created_at': t[5],
                'username': t[6]
            }
        return None

    def add_ticket_reply(self, ticket_id: int, admin_id: int, message: str) -> bool:
        try:
            self.cursor.execute("""
                INSERT INTO ticket_replies (ticket_id, admin_id, message)
                VALUES (?, ?, ?)
            """, (ticket_id, admin_id, message))
            self.cursor.execute("""
                UPDATE tickets SET status = 'answered' WHERE id = ?
            """, (ticket_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding ticket reply: {e}")
            return False
