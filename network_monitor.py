# background_agent/network_monitor.py

import psutil

class NetworkTracker:
    def __init__(self):
        initial = psutil.net_io_counters()
        self.last_sent = initial.bytes_sent
        self.last_recv = initial.bytes_recv

    def get_network_usage(self):
        """
        Calculates the network data consumption (in MB) during the last time interval.
        """
        current = psutil.net_io_counters()
        
        bytes_sent_diff = current.bytes_sent - self.last_sent
        bytes_recv_diff = current.bytes_recv - self.last_recv

        self.last_sent = current.bytes_sent
        self.last_recv = current.bytes_recv

        total_bytes = bytes_sent_diff + bytes_recv_diff
        mb_used = total_bytes / (1024 * 1024)

        return bytes_sent_diff, bytes_recv_diff, round(mb_used, 4)