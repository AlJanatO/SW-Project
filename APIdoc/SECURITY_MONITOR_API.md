# Security Monitor API Documentation

## Overview

The application exposes browser pages and JSON API endpoints for monitoring HTTP activity, analyzing request payloads, checking system health, and viewing dashboard metrics.

## Browser Pages

### `GET /`

Returns the main landing page for the security monitoring system.

### `GET /docs`

Returns an HTML page containing the FastAPI Swagger interface. The underlying Swagger route is mounted at `/swagger`.

### `GET /analyze`

Returns a browser page with preset request buttons and a JSON textarea that submits requests to `/api/analyze`.

### `GET /dashboard`

Returns a browser dashboard that polls `/api/dashboard/metrics` and displays recent request activity, anomaly activity, and a live event timeline.

## API Endpoints

### `GET /api/`

Returns a small status response confirming that the API router is running.

Response shape:

```json
{
  "status": "Security System Running"
}
```

### `POST /api/analyze`

Analyzes a request payload using local detection and optional LLM-assisted analysis.

Request body:

```json
{
  "path": "/login",
  "method": "POST",
  "payload": {
    "username": "admin' OR '1'='1",
    "password": "x"
  },
  "metadata": {}
}
```

Response fields:

- `status`: analysis status string.
- `request_id`: database ID for the stored request when available.
- `session_id`: session identifier used for request tracking.
- `anomaly`: local detection label from `detect_anomaly()`.
- `defense`: action, severity, triggered rule, reason, and recommendation.
- `analysis`: LLM/RAG analysis object containing classification, retrieved context, LLM result, and explanation.

### `GET /api/dashboard/metrics`

Returns dashboard metrics for recent monitoring activity.

Response fields:

- `total_requests_24h`
- `anomaly_requests_24h`
- `top_ips_24h`
- `recent_requests`
- `recent_anomalies`
- `timeline`

### `GET /api/health`

Returns an HTML health check page showing database connectivity, request count, anomaly count, active session count, and LLM configuration status.

### `GET /api/query/{name}`

Runs a registered query from `queries.py` and displays the result in an HTML page.

## Request Validation Models

### `AnalyzeRequest`

- `path`: required string, 1 to 256 characters.
- `method`: required string, 3 to 10 characters.
- `payload`: JSON object, defaults to `{}`.
- `metadata`: JSON object, defaults to `{}`.

### `AnalyzeResponse`

- `status`
- `request_id`
- `session_id`
- `anomaly`
- `defense`
- `analysis`

## LLM Configuration

LLM analysis is optional. If `LLM_API_URL` and `LLM_API_KEY` are not configured, the system keeps running and uses the rule-based detection result.
