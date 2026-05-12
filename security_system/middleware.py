import time
import os
import uuid
from security import detect_anomaly, rate_limit_exceeded
from services import upsert_session, record_request


def _header(scope, name: bytes, default: str = "") -> str:
    for k, v in scope.get("headers", []):
        if k == name:
            try:
                return v.decode("utf-8")
            except Exception:
                return default
    return default


class SecurityMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        ip = (scope.get("client") or ("unknown", 0))[0]
        user_agent = _header(scope, b"user-agent", "unknown")
        cookie_header = _header(scope, b"cookie", "")
        session_id = ""
        for part in cookie_header.split(";"):
            cleaned = part.strip()
            if cleaned.startswith("session_id="):
                session_id = cleaned.split("=", 1)[1]
                break
        if not session_id:
            session_id = _header(scope, b"x-session-id", "")
        new_session = False
        if not session_id:
            session_id = str(uuid.uuid4())
            new_session = True
        session_id = upsert_session(ip, user_agent, session_id)

        max_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
        window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
        actor_key = f"{ip}:{session_id}"
        if rate_limit_exceeded(actor_key, max_requests=max_requests, window_seconds=window_seconds):
            body = b'{"error":"rate_limit_exceeded","message":"Too many requests"}'
            headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode("utf-8"))]
            await send({"type": "http.response.start", "status": 429, "headers": headers})
            await send({"type": "http.response.body", "body": body, "more_body": False})
            record_request(
                session_id=session_id,
                ip=ip,
                endpoint=path,
                method=method,
                payload={"method": method, "path": path},
                status_code=429,
                anomaly_type="Rate Limit Exceeded",
            )
            return

        # Basic request info
        payload = {
            "method": method,
            "path": path,
            "ip": ip,
            "session_id": session_id,
        }

        # Run anomaly detection (real-time)
        risk = detect_anomaly(payload)

        print(f"[MONITOR] {method} {path} → {risk}")
        response_status = 200

        async def send_wrapper(message):
            nonlocal response_status
            if message.get("type") == "http.response.start":
                response_status = message.get("status", 200)
                headers = list(message.get("headers", []))
                if new_session:
                    headers.append((b"set-cookie", f"session_id={session_id}; Path=/; HttpOnly; SameSite=Lax".encode("utf-8")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
        elapsed_ms = int((time.time() - start_time) * 1000)
        record_request(
            session_id=session_id,
            ip=ip,
            endpoint=path,
            method=method,
            payload={"method": method, "path": path, "duration_ms": elapsed_ms},
            status_code=response_status,
            anomaly_type=risk,
        )