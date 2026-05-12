import json
import os
import urllib.request
from db import run_sql


def retrieve_context(payload: dict, ip: str = ""):
    payload_text = json.dumps(payload)
    keyword = payload_text[:80]
    rows = run_sql(
        """
        SELECT endpoint, method, payload, anomaly_type, created_at
        FROM requests
        WHERE ip = %s
           OR CAST(payload AS TEXT) ILIKE %s
        ORDER BY created_at DESC
        LIMIT 8
        """,
        (ip, f"%{keyword}%"),
    )
    events = []
    for row in rows:
        events.append(
            {
                "endpoint": row[0],
                "method": row[1],
                "payload": row[2],
                "anomaly_type": row[3],
                "created_at": str(row[4]),
            }
        )
    return {"similar_events": events}


def _call_external_llm(context: dict):
    api_url = os.getenv("LLM_API_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    if not api_url or not api_key:
        return None

    prompt = (
        "You are a SOC analyst. Classify this request as safe/suspicious/attack, "
        "and return a short explanation as JSON with keys classification and explanation.\n"
        f"Context:\n{json.dumps(context)}"
    )
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a security analyzer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    message = raw["choices"][0]["message"]["content"]
    return {"provider": "external", "raw_output": message}


def analyze_with_llm(payload: dict, ip: str = ""):
    # lazy import prevents circular dependency
    from security import detect_anomaly

    anomaly = detect_anomaly(payload)
    context = retrieve_context(payload, ip=ip)
    external = None
    try:
        external = _call_external_llm({"payload": payload, "context": context})
    except Exception:
        external = None

    return {
        "classification": anomaly,
        "context": context,
        "llm_result": external,
        "explanation": "Request analyzed using security rules with DB-retrieved context"
    }