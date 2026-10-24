# background_agent/tracker.py

import time
from datetime import datetime
from background_agent.app_monitor import get_active_window_details
from background_agent.network_monitor import NetworkTracker
from background_agent.uptime_monitor import get_system_boot_time
from database.db_handler import log_activity, log_network, log_uptime, init_db

def start_background_tracker():
    """
    Runs continuously in the background with real-time tracking (every 2 seconds).
    """
    print("Real-time Background Tracker starting...")
    
    try:
        init_db()
    except Exception as e:
        print(f"Database Init Error: {e}")

    try:
        boot_time = get_system_boot_time()
        print(f"System Boot Time: {boot_time}")
        log_uptime(boot_time=boot_time)
    except Exception as e:
        print(f"Uptime Log Error: {e}")

    network_tracker = NetworkTracker()
    print("Real-time Tracker is active...")

    try:
        while True:
            try:
                # 1. Track Active App (Reduced duration to 2 seconds for real-time update)
                app_name, window_title = get_active_window_details()
                log_activity(app_name, window_title, duration_sec=2)

                # 2. Track Network Usage
                sent, recv, mb_used = network_tracker.get_network_usage()
                log_network(sent, recv, mb_used)

                print(f"[Live Track] App: {app_name} | Data: {mb_used} MB")

            except Exception as inner_error:
                print(f"Error: {inner_error}")

            # 2 seconds interval for high responsiveness / real-time feel
            time.sleep(2)

    except KeyboardInterrupt:
        print("Tracker stopped by user.")

if __name__ == "__main__":
    start_background_tracker()