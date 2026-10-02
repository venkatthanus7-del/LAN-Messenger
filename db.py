import sqlite3
from pathlib import Path

DB_PATH = Path("lan_messenger.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            content TEXT,
            file_name TEXT,
            file_path TEXT,
            msg_type TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
