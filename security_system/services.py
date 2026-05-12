from db import run_sql
from security import detect_anomaly
from llm import analyze_with_llm
from queries import get_query
import json
import uuid


def execute_query(name: str):
    query = get_query(name)
    if not query:
        return {"error": f"Query '{name}' not found"}

    result = run_sql(query)
    return {"query": name, "rows": result}


def upsert_session(ip: str, user_agent: str, session_id: str = "") -> str:
    if not session_id:
        session_id = str(uuid.uuid4())

    existing = run_sql(
        "SELECT session_id FROM sessions WHERE session_id = %s LIMIT 1",
        (session_id,),
    )
    if existing:
        run_sql(
            """
            UPDATE sessions
            SET last_seen = NOW(), request_count = request_count + 1
            WHERE session_id = %s
            """,
            (session_id,),
        )
        return session_id

    run_sql(
        """
        INSERT INTO sessions (session_id, ip, user_agent, first_seen, last_seen, request_count, anomaly_count)
        VALUES (%s, %s, %s, NOW(), NOW(), 1, 0)
        """,
        (session_id, ip, user_agent),
    )
    return session_id


def record_request(
    *,
    session_id: str,
    ip: str,
    endpoint: str,
    method: str,
    payload: dict,
    status_code: int,
    anomaly_type: str = "Normal",
):
    request_result = run_sql(
        """
        INSERT INTO requests (session_id, ip, endpoint, method, payload, status_code, anomaly_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (session_id, ip, endpoint, method, json.dumps(payload), status_code, anomaly_type),
    )
    request_id = request_result[0][0] if request_result else None
    if anomaly_type != "Normal":
        run_sql(
            """
            INSERT INTO anomalies (request_id, session_id, anomaly_type, severity, explanation)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (request_id, session_id, anomaly_type, "medium", "Auto-detected by security layer"),
        )
        run_sql(
            "UPDATE sessions SET anomaly_count = anomaly_count + 1, last_seen = NOW() WHERE session_id = %s",
            (session_id,),
        )
    return request_id


def analyze_request(payload: dict, session_id: str = "", ip: str = ""):
    run_sql(
        "INSERT INTO logs (payload) VALUES (%s)",
        (json.dumps(payload),)
    )

    session_id = session_id or str(uuid.uuid4())
    anomaly = detect_anomaly(payload)
    request_id = record_request(
        session_id=session_id,
        ip=ip or "unknown",
        endpoint=payload.get("path", "/analyze"),
        method=payload.get("method", "POST"),
        payload=payload,
        status_code=200,
        anomaly_type=anomaly,
    )
    analysis = analyze_with_llm(payload, ip=ip)

    return {
        "status": "analyzed",
        "request_id": request_id,
        "session_id": session_id,
        "anomaly": anomaly,
        "analysis": analysis
    }


def get_dashboard_metrics():
    total_requests = run_sql(
        "SELECT COUNT(*) FROM requests WHERE created_at >= NOW() - INTERVAL '24 hours'"
    )[0][0]
    anomaly_requests = run_sql(
        "SELECT COUNT(*) FROM requests WHERE anomaly_type IS NOT NULL AND anomaly_type <> 'Normal' AND created_at >= NOW() - INTERVAL '24 hours'"
    )[0][0]
    top_ips_rows = run_sql(
        """
        SELECT ip, COUNT(*) AS hit_count
        FROM requests
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY ip
        ORDER BY hit_count DESC
        LIMIT 5
        """
    )
    recent_rows = run_sql(
        """
        SELECT created_at, ip, endpoint, method, status_code, anomaly_type
        FROM requests
        ORDER BY created_at DESC
        LIMIT 20
        """
    )
    anomaly_rows = run_sql(
        """
        SELECT created_at, anomaly_type, severity, explanation, session_id
        FROM anomalies
        ORDER BY created_at DESC
        LIMIT 20
        """
    )

    return {
        "total_requests_24h": total_requests,
        "anomaly_requests_24h": anomaly_requests,
        "top_ips_24h": [{"ip": r[0], "hits": r[1]} for r in top_ips_rows],
        "recent_requests": [
            {
                "time": str(r[0]),
                "ip": r[1],
                "endpoint": r[2],
                "method": r[3],
                "status_code": r[4],
                "anomaly_type": r[5],
            }
            for r in recent_rows
        ],
        "recent_anomalies": [
            {
                "time": str(r[0]),
                "anomaly_type": r[1],
                "severity": r[2],
                "explanation": r[3],
                "session_id": r[4],
            }
            for r in anomaly_rows
        ],
    }