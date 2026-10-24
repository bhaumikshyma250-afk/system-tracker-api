# database/models.py

CREATE_UPTIME_TABLE = """
CREATE TABLE IF NOT EXISTS uptime_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boot_time TEXT NOT NULL,
    shutdown_time TEXT,
    session_duration_sec REAL
);
"""

CREATE_ACTIVITY_TABLE = """
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    app_name TEXT NOT NULL,
    window_title TEXT,
    duration_sec INTEGER DEFAULT 5
);
"""

CREATE_NETWORK_TABLE = """
CREATE TABLE IF NOT EXISTS network_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    bytes_sent INTEGER NOT NULL,
    bytes_recv INTEGER NOT NULL,
    mb_used REAL NOT NULL
);
"""