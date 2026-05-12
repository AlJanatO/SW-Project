import json
import logging
import os
import urllib.request
from db import run_sql

log = logging.getLogger(__name__)

VALID_CLASSIFICATIONS = {"safe", "suspicious", "attack"}


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

def _parse_llm_response(raw_text: str) -> dict:
    """Parse the LLM response text into classification and explanation."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    try:
        parsed = json.loads(cleaned)
        classification = str(parsed.get("classification", "")).lower().strip()
        explanation = str(parsed.get("explanation", ""))
        if classification not in VALID_CLASSIFICATIONS:
            classification = "suspicious"
        return {"classification": classification, "explanation": explanation}
    except (json.JSONDecodeError, AttributeError):
        text_lower = raw_text.lower()
        if "attack" in text_lower:
            classification = "attack"
        elif "suspicious" in text_lower:
            classification = "suspicious"
        elif "safe" in text_lower:
            classification = "safe"
        else:
            classification = "suspicious"
        return {"classification": classification, "explanation": raw_text}


def _call_external_llm(context: dict):
    api_url = os.getenv("LLM_API_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    if not api_url or not api_key:
        log.warning("LLM_API_URL or LLM_API_KEY not set — skipping LLM analysis")
        return None

    prompt = (
        "You are a SOC analyst. Classify this API request as safe, suspicious, or attack. "
        "Return ONLY valid JSON with keys \"classification\" (one of: safe, suspicious, attack) "
        "and \"explanation\" (a short sentence).\n"
        f"Context:\n{json.dumps(context)}"
    )
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a security analyzer. Always respond with valid JSON."},
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
    arsed = _parse_llm_response(message)
    return {
        "provider": "external",
        "classification": parsed["classification"],
        "explanation": parsed["explanation"],
        "raw_output": message,
    }


def analyze_with_llm(payload: dict, ip: str = ""):
    from security import detect_anomaly

    rule_anomaly = detect_anomaly(payload)
    context = retrieve_context(payload, ip=ip)

    external = None
    try:
        external = _call_external_llm({"payload": payload, "context": context})
    except Exception as exc:
        log.error("LLM call failed: %s", exc)
        external = None

    if external and external.get("classification"):
        classification = external["classification"]
        explanation = external.get("explanation", "")
    else:
        classification = rule_anomaly
        explanation = "LLM unavailable — classified by rule-based detection"

    return {
        "classification": classification,
        "rule_classification": rule_anomaly,
        "context": context,
        "llm_result": external,
        "explanation": explanation,
    }