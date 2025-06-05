# apple_id_bot/database/models.py

import sqlite3
from datetime import datetime

DB_NAME = "apple_id_bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_APPLE_IDS_TABLE = """
CREATE TABLE IF NOT EXISTS apple_ids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    email_password TEXT,
    birth_date TEXT,
    security_questions TEXT,
    status TEXT CHECK(status IN ('available', 'sold')) DEFAULT 'available',
    sold_to INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sold_to) REFERENCES users(user_id) ON DELETE SET NULL
);
"""

CREATE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    type TEXT CHECK(type IN ('charge', 'purchase', 'refund')) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

CREATE_TICKETS_TABLE = """
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    status TEXT CHECK(status IN ('open', 'closed')) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_USERS_TABLE)
    cursor.execute(CREATE_APPLE_IDS_TABLE)
    cursor.execute(CREATE_TRANSACTIONS_TABLE)
    cursor.execute(CREATE_TICKETS_TABLE)
    conn.commit()
    conn.close()
