# Acceptance Tests for Security Monitoring System

## Purpose

This document describes the manual acceptance tests for the FastAPI security monitoring system. The tests cover the main user-facing pages, request analysis workflow, local attack detection, optional LLM fallback behavior, dashboard metrics, and generated API documentation.

## Test Environment

- Application: FastAPI Security Monitoring System
- Runtime command: `python -m uvicorn main:app --reload`
- Test runner: `python -m pytest test_security.py -v`
- Browser URLs:
  - `http://127.0.0.1:8000/`
  - `http://127.0.0.1:8000/analyze`
  - `http://127.0.0.1:8000/dashboard`
  - `http://127.0.0.1:8000/api/health`
  - `http://127.0.0.1:8000/docs`
- Test data source: manual JSON payloads submitted through the `/analyze` page or `/api/analyze` endpoint

## AT-1: Application Starts Successfully

### Objective

Verify that the FastAPI application starts and serves the main page.

### Steps

1. Start the app.
2. Open `http://127.0.0.1:8000/`.

### Expected Result

The main page loads successfully and introduces the security monitoring system.

## AT-2: Normal Request Is Accepted

### Objective

Verify that normal user behavior is not flagged as an attack.

### Input

```json
{
  "path": "/login",
  "method": "POST",
  "payload": {
    "username": "student",
    "password": "normal-password"
  }
}
```

### Expected Result

The system should classify the request as normal or safe.

## AT-3: SQL Injection Is Detected

### Objective

Verify that the system detects SQL injection attempts.

### Input

```json
{
  "path": "/login",
  "method": "POST",
  "payload": {
    "username": "admin' OR '1'='1",
    "password": "x"
  }
}
```

### Expected Result

The system should flag the request as a SQL injection attempt.

## AT-4: XSS Attempt Is Detected

### Objective

Verify that the system detects XSS payloads.

### Input

```json
{
  "path": "/comment",
  "method": "POST",
  "payload": {
    "message": "<script>alert('xss')</script>"
  }
}
```

### Expected Result

The system should flag the request as an XSS attempt.

## AT-5: Flood-Like Payload Is Detected

### Objective

Verify that unusually large payloads are flagged.

### Input

Submit a request with a payload field containing a string longer than the flood threshold used by `detect_anomaly()`.

Example structure:

```json
{
  "path": "/upload",
  "method": "POST",
  "payload": {
    "content": "large repeated string"
  }
}
```

### Expected Result

The system should flag the request as a possible flood attack.

## AT-6: LLM/RAG Analysis Returns Contextual Output

### Objective

Verify that `/api/analyze` returns an analysis object containing retrieved context and LLM result information.

### Steps

1. Configure `LLM_API_URL`, `LLM_API_KEY`, and `LLM_MODEL` if available.
2. Submit a payload through `/analyze`.
3. Inspect the returned `analysis` object.

### Expected Result

The response includes:

- `classification`
- `context`
- `llm_result`
- `explanation`

If the LLM is unavailable, the system should fall back gracefully.

### Notes

During local testing, the LLM provider may return a rate-limit response such as HTTP 429. That result is acceptable as long as the application returns a normal API response and falls back instead of crashing.

## AT-7: Health Check Shows Component Status

### Objective

Verify that the health endpoint reports database and LLM configuration status.

### Steps

1. Open `http://127.0.0.1:8000/api/health`.

### Expected Result

The page shows database status, request count, anomaly count, active sessions, and LLM configuration status.

## AT-8: Dashboard Shows Activity

### Objective

Verify that logged requests and anomalies are visible through dashboard metrics.

### Steps

1. Submit normal and attack requests.
2. Open `http://127.0.0.1:8000/dashboard`.

### Expected Result

The dashboard shows recent request and anomaly activity.

## AT-9: FastAPI API Documentation Is Available

### Objective

Verify that generated API documentation is available.

### Steps

1. Open `http://127.0.0.1:8000/docs`.

### Expected Result

Swagger/OpenAPI documentation displays available API endpoints.

## AT-10: Routing Upgrade Demo

### Objective

After the routing upgrade is implemented, verify that ambiguous security-sensitive requests are routed to the LLM instead of being treated exactly like clear local detections.

### Input

```json
{
  "path": "/review",
  "method": "POST",
  "payload": {
    "message": "please review this admin token behavior"
  }
}
```

### Expected Result After Routing Upgrade

The response should show that LLM routing was required and attempted.

Expected evidence fields after upgrade:

- `requires_llm`
- `llm_required`
- `llm_attempted`
- `llm_used`
- `llm_error`

## Test Results Summary

### Pass Criteria

- The app starts without startup errors.
- Normal traffic is not labeled as a known attack.
- SQL injection and XSS payloads are detected.
- LLM unavailability does not crash `/api/analyze`.
- Health and dashboard pages load.
- FastAPI documentation is visible at `/docs`.
