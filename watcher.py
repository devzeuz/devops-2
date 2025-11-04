#!/usr/bin/env python3
import os
import time
import re
from collections import deque
from datetime import datetime
import requests


LOG_FILE = "/var/log/nginx/access.log"
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", "200"))
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "2"))
ALERT_COOLDOWN_SEC = int(os.getenv("ALERT_COOLDOWN_SEC", "300"))
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "0") == "1"
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


last_pool = None
request_window = deque(maxlen=WINDOW_SIZE)
last_alert_time = 0


LOG_REGEX = re.compile(
    r".*pool=(?P<pool>\w+).*status=(?P<status>\d+).*"
)

def send_slack_alert(failover_from=None, failover_to=None, error_rate=None, threshold=None, window=None):
    """Send combined Slack alert"""
    if MAINTENANCE_MODE:
        print("[INFO] Maintenance mode ON — skipping Slack alert")
        return

    message_lines = []

    if failover_from and failover_to:
        message_lines.append(f"Failover detected: {failover_from} -> {failover_to}")

    if error_rate is not None and threshold is not None:
        message_lines.append(f"Error Rate: {error_rate:.2f}% (threshold: {threshold}%)")
        if window:
            message_lines.append(f"Window: {window['errors']} errors in {window['total']} requests")

    message_lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    payload = {
        "text": ":rotating_light: Blue-Green Deployment Alert\n" + "\n".join(message_lines)
    }

    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload)
        resp.raise_for_status()
        print(f"[INFO] Slack alert sent successfully")
    except Exception as e:
        print(f"[ERROR] Slack alert failed: {e}")

def tail_log(file):
    """Generator to tail a file"""
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def main():
    global last_pool, last_alert_time

    if not SLACK_WEBHOOK_URL:
        print("[ERROR] SLACK_WEBHOOK_URL not set. Exiting.")
        return

    with open(LOG_FILE, "r") as f:
        log_lines = tail_log(f)

        for line in log_lines:
            m = LOG_REGEX.search(line)
            if not m:
                continue

            pool = m.group("pool")
            status = int(m.group("status"))

            # Track request window
            request_window.append(status)
            total_requests = len(request_window)
            errors = sum(1 for s in request_window if s >= 500)
            error_rate = (errors / total_requests) * 100 if total_requests > 0 else 0

            # Check failover
            failover_event = None
            if last_pool and pool != last_pool:
                failover_event = (last_pool, pool)
                last_pool = pool
            elif last_pool is None:
                last_pool = pool

            # Alert cooldown
            now = time.time()
            if failover_event or (error_rate > ERROR_RATE_THRESHOLD and total_requests == WINDOW_SIZE):
                if now - last_alert_time >= ALERT_COOLDOWN_SEC:
                    send_slack_alert(
                        failover_from=failover_event[0] if failover_event else None,
                        failover_to=failover_event[1] if failover_event else None,
                        error_rate=error_rate if error_rate > ERROR_RATE_THRESHOLD else None,
                        threshold=ERROR_RATE_THRESHOLD,
                        window={"errors": errors, "total": total_requests} if error_rate > ERROR_RATE_THRESHOLD else None
                    )
                    last_alert_time = now

if __name__ == "__main__":
    print("[INFO] Starting Blue-Green log watcher...")
    main()

