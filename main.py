# backend/main.py

from fastapi import FastAPI
import sqlite3
import os

app = FastAPI(title="System Tracker API")

# আপনার মূল ডাটাবেসের পাথ
DB_PATH = os.path.join(os.path.dirname(__file__), 'tracker_data.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def home():
    return {"message": "System Tracker API is running live!"}

@app.get("/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total activity logs count
    cursor.execute("SELECT COUNT(*) as total_logs FROM activity_logs")
    total_logs = cursor.fetchone()["total_logs"]
    
    # Total network bandwidth used
    cursor.execute("SELECT SUM(mb_used) as total_mb FROM network_logs")
    res = cursor.fetchone()["total_mb"]
    total_mb = round(res, 2) if res else 0.0
    
    # Unique apps count
    cursor.execute("SELECT COUNT(DISTINCT app_name) as unique_apps FROM activity_logs")
    unique_apps = cursor.fetchone()["unique_apps"]
    
    conn.close()
    
    return {
        "total_logs": total_logs,
        "total_data_mb": total_mb,
        "unique_apps": unique_apps
    }
