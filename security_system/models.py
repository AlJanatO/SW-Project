from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    # This model is the request shape used by the demo analyze page and API tests.
    path: str = Field(..., min_length=1, max_length=256)
    method: str = Field(..., min_length=3, max_length=10)
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    # The response separates detection, defense, and LLM analysis so the UI can explain each part.
    status: str
    request_id: Optional[int] = None
    session_id: str
    anomaly: str
    defense: Dict[str, Any]
    analysis: Dict[str, Any]


class DashboardMetricsResponse(BaseModel):
    # The dashboard combines summary cards, recent tables, and the live attack timeline.
    total_requests_24h: int
    anomaly_requests_24h: int
    top_ips_24h: List[Dict[str, Any]]
    recent_requests: List[Dict[str, Any]]
    recent_anomalies: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
