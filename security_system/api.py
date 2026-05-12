from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services import execute_query, analyze_request, get_dashboard_metrics
from ui import layout
from models import AnalyzeRequest, AnalyzeResponse, DashboardMetricsResponse
from db import run_sql

router = APIRouter()

@router.get("/")
def root():
    return {"status": "Security System Running"}


@router.get("/query/{name}", response_class=HTMLResponse)
def run_query(name: str):
    result = execute_query(name)

    return layout(f"""
        <h2>Query Result: {name}</h2>
        <div class="card">
            <pre>{result}</pre>
        </div>
    """)

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest, request: Request):
    session_id = request.cookies.get("session_id", "")
    ip = request.client.host if request.client else "unknown"
    return analyze_request(payload.model_dump(), session_id=session_id, ip=ip)


@router.get("/dashboard/metrics", response_model=DashboardMetricsResponse)
def dashboard_metrics():
    return get_dashboard_metrics()

@router.get("/health", response_class=HTMLResponse)
def health_check():
    checks = {}

    # Database connectivity
    try:
        result = run_sql("SELECT NOW()")
        db_time = str(result[0][0]) if result else "unknown"
        checks["database"] = {"status": "connected", "server_time": db_time}
    except Exception as e:
        checks["database"] = {"status": "disconnected", "error": str(e)}

    # Total requests logged
    try:
        total = run_sql("SELECT COUNT(*) FROM requests")[0][0]
        checks["requests_logged"] = total
    except Exception:
        checks["requests_logged"] = "error"

    # Total anomalies detected
    try:
        anomalies = run_sql("SELECT COUNT(*) FROM anomalies")[0][0]
        checks["anomalies_detected"] = anomalies
    except Exception:
        checks["anomalies_detected"] = "error"

    # Active sessions
    try:
        sessions = run_sql("SELECT COUNT(*) FROM sessions")[0][0]
        checks["active_sessions"] = sessions
    except Exception:
        checks["active_sessions"] = "error"

    # LLM status
    import os
    llm_url = os.getenv("LLM_API_URL", "").strip()
    llm_key = os.getenv("LLM_API_KEY", "").strip()
    if llm_url and llm_key:
        checks["llm"] = {"status": "configured", "api_url": llm_url}
    else:
        checks["llm"] = {"status": "not configured"}

    db_ok = checks["database"].get("status") == "connected"
    overall = "healthy" if db_ok else "unhealthy"

    import json
    return layout(f"""
        <h2>System Health Check</h2>
        <div class="card">
            <div><strong>Overall Status:</strong> {overall}</div>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Component Details</h3>
            <pre>{json.dumps(checks, indent=2)}</pre>
        </div>
    """)