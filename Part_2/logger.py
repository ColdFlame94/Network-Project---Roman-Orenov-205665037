import csv
from datetime import datetime
from threading import Lock

class ChatLogger:
    def __init__(self, filename="chat_logs.csv"):
        self.filename = filename
        self.lock = Lock()

        # create file with header if not exists
        with open(self.filename, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["date", "time", "client_name", "message"])

    def log_message(self, client_name: str, message: str):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        with self.lock:
            with open(self.filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([date_str, time_str, client_name, message])
