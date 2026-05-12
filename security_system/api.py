from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services import execute_query, analyze_request, get_dashboard_metrics
from ui import layout
from models import AnalyzeRequest, AnalyzeResponse, DashboardMetricsResponse

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