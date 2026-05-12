from datetime import datetime, timedelta, timezone
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
 
    # SQL Injection patterns
    sql_patterns = [
        "select ", "drop ", "insert ", "delete ", "update ",
        "union ", "' or '1'='1", "' or 1=1", "'; --", "' --",
        "1=1", "or 1=1", "/*", "*/", "xp_", "exec(",
        "char(", "cast(", "convert(", "@@version",
    ]
    for pattern in sql_patterns:
        if pattern in text:
            return "SQL Injection Attempt"
 
    # XSS patterns
    xss_patterns = ["<script", "javascript:", "onerror=", "onload=", "onclick=", "alert(", "eval("]
    for pattern in xss_patterns:
        if pattern in text:
            return "XSS Attempt"
 
    # Path traversal
    if "../" in text or "..%2f" in text or "%2e%2e" in text:
        return "Path Traversal Attempt"
 
    # Command injection
    cmd_patterns = ["; ls", "; cat", "| cat", "`cat", "$(", "; rm", "| rm"]
    for pattern in cmd_patterns:
        if pattern in text:
            return "Command Injection Attempt"
 
    # Recursive API abuse
    if ("http://" in text or "https://" in text) and "/vuln/recursive" in text:
        return "Recursive API Abuse"
 
    # Flood attack
    if len(text) > 1500:
        return "Possible Flood Attack"
 
    return "Normal"


def rate_limit_exceeded(actor_key: str, max_requests: int, window_seconds: int) -> bool:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)
    bucket = REQUEST_WINDOWS[actor_key]
    bucket[:] = [ts for ts in bucket if ts >= window_start]
    bucket.append(now)
    return len(bucket) > max_requests