import json
import logging
import math
import os
import ssl
import re
import urllib.request

import certifi

from db import ensure_schema, run_sql

ssl_context = ssl.create_default_context(cafile=certifi.where())

log = logging.getLogger(__name__)

VALID_CLASSIFICATIONS = {"safe", "suspicious", "attack"}
EMBEDDING_DIMENSIONS = 32


def generate_payload_embedding(payload: dict) -> list[float]:
    payload_text = json.dumps(payload, sort_keys=True).lower()
    tokens = re.findall(r"[a-z0-9_./'=-]+", payload_text)
    vector = [0.0] * EMBEDDING_DIMENSIONS
    for token in tokens:
        bucket = sum(ord(char) for char in token) % EMBEDDING_DIMENSIONS
        vector[bucket] += 1.0
    magnitude = math.sqrt(sum(value * value for value in vector))
    if not magnitude:
        return vector
    return [round(value / magnitude, 6) for value in vector]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def retrieve_context(payload: dict, ip: str = ""):
    ensure_schema()
    query_embedding = generate_payload_embedding(payload)
    rows = run_sql(
        """
        SELECT endpoint, method, payload, anomaly_type, created_at, payload_embedding
        FROM requests
        WHERE payload_embedding IS NOT NULL
           OR ip = %s
        ORDER BY created_at DESC
        LIMIT 50
        """,
        (ip,),
    )
    ranked_events = []
    for row in rows:
        stored_embedding = row[5] or []
        similarity = _cosine_similarity(query_embedding, stored_embedding)
        if ip and similarity == 0.0:
            similarity = 0.05
        ranked_events.append(
            {
                "endpoint": row[0],
                "method": row[1],
                "payload": row[2],
                "anomaly_type": row[3],
                "created_at": str(row[4]),
                "similarity": round(similarity, 4),
            }
        )
    ranked_events.sort(key=lambda event: event["similarity"], reverse=True)
    return {
        "retrieval_method": "local-vector-cosine",
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "similar_events": ranked_events[:8],
    }

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
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, timeout=12, context=ssl_context) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    message = raw["choices"][0]["message"]["content"]
    parsed = _parse_llm_response(message)
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