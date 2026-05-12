from datetime import datetime, timedelta
from collections import defaultdict

LOG_STORE = []
REQUEST_WINDOWS = defaultdict(list)


def log_request(payload: dict):
    LOG_STORE.append({
        "payload": payload,
        "time": datetime.now()
    })


def detect_anomaly(payload: dict):
    text = str(payload).lower()

    if "select " in text or "drop " in text or "' or '1'='1" in text:
        return "SQL Injection Attempt"

    if "http://" in text or "https://" in text and "/vuln/recursive" in text:
        return "Recursive API Abuse"

    if len(text) > 1500:
        return "Possible Flood Attack"

    return "Normal"


def rate_limit_exceeded(actor_key: str, max_requests: int, window_seconds: int) -> bool:
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_seconds)
    bucket = REQUEST_WINDOWS[actor_key]
    bucket[:] = [ts for ts in bucket if ts >= window_start]
    bucket.append(now)
    return len(bucket) > max_requests