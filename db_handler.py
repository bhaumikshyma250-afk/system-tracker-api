# database/db_handler.py

import sqlite3
import os
from datetime import datetime
from database.models import CREATE_UPTIME_TABLE, CREATE_ACTIVITY_TABLE, CREATE_NETWORK_TABLE

DB_PATH = os.path.join(os.path.dirname(__file__), 'tracker_data.db')

def get_connection():
    """Creates and returns an SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all required database tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_UPTIME_TABLE)
        cursor.execute(CREATE_ACTIVITY_TABLE)
        cursor.execute(CREATE_NETWORK_TABLE)
        conn.commit()

def log_activity(app_name, window_title, duration_sec=5):
    """Saves active application and window activity details."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (timestamp, app_name, window_title, duration_sec) VALUES (?, ?, ?, ?)",
            (timestamp, app_name, window_title, duration_sec)
        )
        conn.commit()

def log_network(bytes_sent, bytes_recv, mb_used):
    """Saves network data consumption metrics."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO network_logs (timestamp, bytes_sent, bytes_recv, mb_used) VALUES (?, ?, ?, ?)",
            (timestamp, bytes_sent, bytes_recv, mb_used)
        )
        conn.commit()

def log_uptime(boot_time, shutdown_time=None, duration=None):
    """Saves system boot and session duration details."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO uptime_logs (boot_time, shutdown_time, session_duration_sec) VALUES (?, ?, ?)",
            (boot_time, shutdown_time, duration)
        )
        conn.commit()