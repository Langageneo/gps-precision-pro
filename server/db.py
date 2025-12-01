# server/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "analytics.sqlite"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS gps_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        lat REAL,
        lon REAL,
        accuracy REAL,
        source TEXT,
        timestamp INTEGER,
        corrected_lat REAL,
        corrected_lon REAL,
        correction_reason TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_device_time ON gps_points(device_id, timestamp);
    CREATE TABLE IF NOT EXISTS address_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT UNIQUE,
        lat REAL,
        lon REAL,
        display_name TEXT,
        timestamp INTEGER
    );
    CREATE TABLE IF NOT EXISTS analytics_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT,
        value TEXT,
        timestamp INTEGER
    );
    """)
    conn.commit()
    conn.close()

# initialize on import
init_db()
