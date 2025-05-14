import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.token = os.getenv("BOT_TOKEN")
        self.database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3")
        self.admins = [int(i) for i in os.getenv("ADMINS", "").split(",") if i.strip().isdigit()]

def load_config():
    return Config()
