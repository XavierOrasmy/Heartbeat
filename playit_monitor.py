import os
import time
import subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# SETTINGS
PING_TARGET = "8.8.8.8"  # Replace with your server IP if desired.
CHECK_INTERVAL = 30  # Seconds between checks
FAIL_THRESHOLD = 3
SERVICE_NAME = "playit"
LOG_FOLDER = "folerder/smallfolder" # insert folder location
LOG_RETENTION_DAYS = 7  # Keep logs for 7 days

# Ensure log folder exists
os.makedirs(LOG_FOLDER, exist_ok=True)

def get_log_file():
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%m-%d-%Y")
    return os.path.join(LOG_FOLDER, f"{today}.log")

def log_to_file(message):
    log_file = get_log_file()
    with open(log_file, "a") as f:
        f.write(message + "\n")

def log_console(message):
    timestamp = datetime.now(ZoneInfo("America/New_York")).strftime("%m-%d-%Y %I:%M:%S %p %Z")
    print(f"[{timestamp}] {message}")

def ping():
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "2", PING_TARGET], capture_output=True, text=True)
        output = result.stdout
        if "time=" in output:
            time_ms = output.split("time=")[1].split(" ms")[0]
            return True, float(time_ms)
        return True, None
    except subprocess.CalledProcessError:
        return False, None

def restart_service():
    log_console(f"Restarting {SERVICE_NAME} service...")
    os.system(f"systemctl restart {SERVICE_NAME}")

def clean_old_logs():
    cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    for filename in os.listdir(LOG_FOLDER):
        if filename.endswith(".log"):
            filepath = os.path.join(LOG_FOLDER, filename)
            try:
                file_date = datetime.strptime(filename.replace(".log", ""), "%m-%d-%Y")
                if file_date < cutoff:
                    os.remove(filepath)
                    log_console(f"Deleted old log file: {filename}")
            except Exception:
                continue  # Skip files that don’t match date format

def main():
    fails = 0
    was_offline = False

    while True:
        clean_old_logs()

        success, ping_time = ping()

        if success:
            if was_offline:
                message = "Connection Restored"
                log_console(message)
                log_to_file(message)
                was_offline = False

            if ping_time:
                log_console(f"Online - Ping {ping_time:.2f}ms")
            else:
                log_console("Online - Ping (no time)")

            fails = 0

        else:
            message = "OFFLINE - Connection Lost"
            log_console(message)
            log_to_file(message)
            was_offline = True
            fails += 1

            if fails >= FAIL_THRESHOLD:
                restart_service()
                fails = 0

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
