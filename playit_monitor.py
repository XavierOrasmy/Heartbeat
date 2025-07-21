import os
import time
import subprocess

# SETTINGS
PING_TARGET = "8.8.8.8"  # Google DNS
CHECK_INTERVAL = 10
FAIL_THRESHOLD = 3       # failed pings
SERVICE_NAME = "playit"

def ping():
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "2", PING_TARGET])
        return True
    except subprocess.CalledProcessError:
        return False

def restart_service():
    print(f"[!] Restarting {SERVICE_NAME} service...")
    os.system(f"systemctl restart {SERVICE_NAME}")

def main():
    fails = 0
    while True:
        if ping():
            print("[+] Internet OK")
            fails = 0
        else:
            print("[!] Ping failed")
            fails += 1

        if fails >= FAIL_THRESHOLD:
            restart_service()
            fails = 0

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
