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
    # This is the local detection layer documented in the SRS. It keeps the demo reliable
    # because clear attacks are caught without needing an external LLM service.
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


def build_defense(anomaly_type: str):
    # This turns a detection label into a response the user can actually understand in the demo.
    # The dashboard and analyze page both use these fields to show what action the system took.
    defenses = {
        "SQL Injection Attempt": {
            "action": "blocked",
            "severity": "critical",
            "rule": "SQL injection pattern detected",
            "reason": "The request matched a known SQL injection pattern such as OR 1=1, UNION, DROP, or SQL comments.",
            "recommendation": "Use parameterized queries and validate login/search inputs before they reach the database.",
        },
        "XSS Attempt": {
            "action": "blocked",
            "severity": "high",
            "rule": "Cross-site scripting pattern detected",
            "reason": "The request contained script or browser event-handler content that could run in another user's browser.",
            "recommendation": "Escape output, sanitize stored text, and reject script tags in user-submitted fields.",
        },
        "Path Traversal Attempt": {
            "action": "blocked",
            "severity": "high",
            "rule": "Path traversal pattern detected",
            "reason": "The request tried to reference parent directories using traversal characters.",
            "recommendation": "Normalize file paths and restrict file access to an approved application directory.",
        },
        "Command Injection Attempt": {
            "action": "blocked",
            "severity": "critical",
            "rule": "Command injection pattern detected",
            "reason": "The request contained shell separators or command-substitution syntax.",
            "recommendation": "Avoid shell execution for user input and use safe library calls instead of command strings.",
        },
        "Recursive API Abuse": {
            "action": "blocked",
            "severity": "medium",
            "rule": "Recursive API call pattern detected",
            "reason": "The request referenced the vulnerable recursive endpoint and could create repeated server calls.",
            "recommendation": "Limit outbound callbacks, validate target URLs, and keep recursive simulation endpoints disabled by default.",
        },
        "Possible Flood Attack": {
            "action": "blocked",
            "severity": "medium",
            "rule": "Oversized payload detected",
            "reason": "The request body was large enough to look like a flooding or resource exhaustion attempt.",
            "recommendation": "Set request body limits and reject unusually large payloads before deeper processing.",
        },
        "Rate Limit Exceeded": {
            "action": "blocked",
            "severity": "medium",
            "rule": "Rate limit exceeded",
            "reason": "The same actor sent too many requests during the configured time window.",
            "recommendation": "Keep rate limits enabled and tune the threshold for the expected demo or production traffic.",
        },
    }
    return defenses.get(anomaly_type, {
        "action": "allowed",
        "severity": "low",
        "rule": "No attack pattern detected",
        "reason": "The request did not match the current local attack signatures.",
        "recommendation": "Continue monitoring and review unusual activity on the dashboard.",
    })


def rate_limit_exceeded(actor_key: str, max_requests: int, window_seconds: int) -> bool:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)
    bucket = REQUEST_WINDOWS[actor_key]
    bucket[:] = [ts for ts in bucket if ts >= window_start]
    bucket.append(now)
    return len(bucket) > max_requests