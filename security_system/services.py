import json
import uuid

from db import ensure_schema, run_sql
from llm import analyze_with_llm, generate_payload_embedding
from queries import get_query
from security import build_defense, detect_anomaly

SCHEMA_READY = False


def _ensure_runtime_schema():
    global SCHEMA_READY
    if not SCHEMA_READY:
        ensure_schema()
        SCHEMA_READY = True


def execute_query(name: str):
    # Named queries support simple evidence views without accepting raw SQL from the browser.
    query = get_query(name)
    if not query:
        return {"error": f"Query '{name}' not found"}
 
    _ensure_runtime_schema()
    result = run_sql(query)
    rows = []
    for row in result:
        rows.append(tuple(str(col) if hasattr(col, "isoformat") else col for col in row))
    return {"query": name, "rows": rows}


def upsert_session(ip: str, user_agent: str, session_id: str = "") -> str:
    # Session records connect multiple monitored requests to the same browser/client.
    if not session_id:
        session_id = str(uuid.uuid4())

    _ensure_runtime_schema()
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
    analysis_source: str = "rule-based",
    llm_used: bool = False,
):
    # requests is the main audit table. It stores normal and attack traffic once so the
    # dashboard can show a clean traffic story instead of duplicate log rows.
    _ensure_runtime_schema()
    defense = build_defense(anomaly_type)
    payload_embedding = generate_payload_embedding(payload)
    request_result = run_sql(
        """
        INSERT INTO requests (session_id, ip, endpoint, method, payload, status_code, anomaly_type, analysis_source, llm_used, payload_embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (session_id, ip, endpoint, method, json.dumps(payload), status_code, anomaly_type, analysis_source, llm_used, json.dumps(payload_embedding)),
    )
    request_id = request_result[0][0] if request_result else None
    if anomaly_type != "Normal":
        run_sql(
            """
            INSERT INTO anomalies (request_id, session_id, anomaly_type, severity, action, rule, explanation, recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                request_id,
                session_id,
                anomaly_type,
                defense["severity"],
                defense["action"],
                defense["rule"],
                defense["reason"],
                defense["recommendation"],
            ),
        )
        run_sql(
            "UPDATE sessions SET anomaly_count = anomaly_count + 1, last_seen = NOW() WHERE session_id = %s",
            (session_id,),
        )
    return request_id


def analyze_request(payload: dict, session_id: str = "", ip: str = ""):
    # /api/analyze is the controlled demo path: it records the request, returns a defense
    # action, and adds optional LLM/RAG explanation if an LLM provider is configured.
    session_id = session_id or str(uuid.uuid4())
    upsert_session(ip or "unknown", "api-client", session_id)
    anomaly = detect_anomaly(payload)
    defense = build_defense(anomaly)
    analysis = analyze_with_llm(payload, ip=ip)
    llm_used = bool(analysis.get("llm_result"))
    analysis_source = "llm" if llm_used else "rule-based"
    request_id = record_request(
        session_id=session_id,
        ip=ip or "unknown",
        endpoint=payload.get("path", "/analyze"),
        method=payload.get("method", "POST"),
        payload=payload,
        status_code=200,
        anomaly_type=anomaly,
        analysis_source=analysis_source,
        llm_used=llm_used,
    )

    return {
        "status": "analyzed",
        "request_id": request_id,
        "session_id": session_id,
        "anomaly": anomaly,
        "defense": defense,
        "analysis": analysis
    }


def get_dashboard_metrics():
    # The dashboard uses one service call so the browser never connects directly to PostgreSQL.
    _ensure_runtime_schema()
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
        SELECT created_at, ip, endpoint, method, status_code, anomaly_type, analysis_source
        FROM requests
        ORDER BY created_at DESC
        LIMIT 20
        """
    )
    anomaly_rows = run_sql(
        """
        SELECT created_at, anomaly_type, severity, explanation, session_id, action, rule, recommendation
        FROM anomalies
        ORDER BY created_at DESC
        LIMIT 20
        """
    )
    timeline_rows = run_sql(
        """
        SELECT id, created_at, endpoint, method, status_code, anomaly_type, payload, analysis_source, llm_used
        FROM requests
        WHERE created_at >= NOW() - INTERVAL '60 minutes'
        ORDER BY created_at ASC
        LIMIT 100
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
                "analysis_source": r[6],
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
                "action": r[5],
                "rule": r[6],
                "recommendation": r[7],
            }
            for r in anomaly_rows
        ],
        "timeline": [
            {
                "request_id": r[0],
                "time": str(r[1]),
                "endpoint": r[2],
                "method": r[3],
                "status_code": r[4],
                "anomaly_type": r[5] or "Normal",
                "severity": build_defense(r[5] or "Normal")["severity"],
                "defense_action": build_defense(r[5] or "Normal")["action"],
                "payload": r[6],
                "analysis_source": r[7],
                "llm_used": r[8],
            }
            for r in timeline_rows
        ],
    }