# apple_id_bot/database/db_handler.py

import sqlite3
from typing import Dict, List, Any
from config.config import DATABASE_PATH
from database.models import *

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self.initialize_tables()
    
    def initialize_tables(self):
        """ایجاد جداول اولیه"""
        self.cursor.execute(CREATE_USERS_TABLE)
        self.cursor.execute(CREATE_APPLE_IDS_TABLE)
        self.cursor.execute(CREATE_TRANSACTIONS_TABLE)
        self.cursor.execute(CREATE_TICKETS_TABLE)
        self.conn.commit()

    def add_user(self, user_id: int, username: str) -> None:
        """افزودن کاربر جدید"""
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        self.conn.commit()

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """دریافت اطلاعات کاربر"""
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
                "is_admin": result[3],
                "created_at": result[4]
            }
        return None

# اضافه کردن به کلاس DatabaseManager

def add_apple_id(self, data: dict) -> bool:
    """افزودن اپل آیدی جدید"""
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

def get_all_users(self) -> List[Dict]:
    """دریافت لیست همه کاربران"""
    self.cursor.execute("SELECT * FROM users")
    users = self.cursor.fetchall()
    return [{"user_id": user[0], "username": user[1], "balance": user[2]} for user in users]

def update_balance(self, user_id: int, amount: int) -> bool:
    """بروزرسانی موجودی کاربر"""
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

# اضافه کردن به کلاس DatabaseManager

def create_ticket(self, user_id: int, title: str, message: str) -> int:
    """ایجاد تیکت جدید"""
    self.cursor.execute("""
        INSERT INTO tickets (user_id, title, message, status)
        VALUES (?, ?, ?, 'open')
    """, (user_id, title, message))
    self.conn.commit()
    return self.cursor.lastrowid

def get_user_tickets(self, user_id: int) -> List[Dict]:
    """دریافت لیست تیکت‌های کاربر"""
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

def get_ticket(self, ticket_id: int) -> Dict:
    """دریافت جزئیات یک تیکت"""
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
    """افزودن پاسخ به تیکت"""
    try:
        self.cursor.execute("""
            INSERT INTO ticket_replies (ticket_id, admin_id, message)
            VALUES (?, ?, ?)
        """, (ticket_id, admin_id, message))
        
        self.cursor.execute("""
            UPDATE tickets
            SET status = 'answered'
            WHERE id = ?
        """, (ticket_id,))
        
        self.conn.commit()
        return True
    except Exception as e:
        print(f"Error adding ticket reply: {e}")
        return False
