from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    path: str = Field(..., min_length=1, max_length=256)
    method: str = Field(..., min_length=3, max_length=10)
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    status: str
    request_id: Optional[int]
    session_id: str
    anomaly: str
    analysis: Dict[str, Any]


class DashboardMetricsResponse(BaseModel):
    total_requests_24h: int
    anomaly_requests_24h: int
    top_ips_24h: List[Dict[str, Any]]
    recent_requests: List[Dict[str, Any]]
    recent_anomalies: List[Dict[str, Any]]
