# Acceptance Tests

## Purpose

This document defines acceptance tests for the security monitoring system. Each acceptance test should be executed manually before final submission and illustrated with screenshots.

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

## AT-1: Application Starts Successfully

### Objective

Verify that the FastAPI application starts and serves the main page.

### Steps

1. Start the app.
2. Open `http://127.0.0.1:8000/`.

### Expected Result

The main page loads successfully and introduces the security monitoring system.

### Screenshot

TODO: Add screenshot of the main page.

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

### Screenshot

TODO: Add screenshot of the `/analyze` result.

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

### Screenshot

TODO: Add screenshot of the SQL injection result.

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

### Screenshot

TODO: Add screenshot of the XSS result.

## AT-5: Flood-Like Payload Is Detected

### Objective

Verify that unusually large payloads are flagged.

### Input

Submit a request containing a very large string payload.

### Expected Result

The system should flag the request as a possible flood attack.

### Screenshot

TODO: Add screenshot of the flood detection result.

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

### Screenshot

TODO: Add screenshot of LLM analysis or fallback.

## AT-7: Health Check Shows Component Status

### Objective

Verify that the health endpoint reports database and LLM configuration status.

### Steps

1. Open `http://127.0.0.1:8000/api/health`.

### Expected Result

The page shows database status, request count, anomaly count, active sessions, and LLM configuration status.

### Screenshot

TODO: Add screenshot of health check.

## AT-8: Dashboard Shows Activity

### Objective

Verify that logged requests and anomalies are visible through dashboard metrics.

### Steps

1. Submit normal and attack requests.
2. Open `http://127.0.0.1:8000/dashboard`.

### Expected Result

The dashboard shows recent request and anomaly activity.

### Screenshot

TODO: Add screenshot of dashboard.

## AT-9: FastAPI API Documentation Is Available

### Objective

Verify that generated API documentation is available.

### Steps

1. Open `http://127.0.0.1:8000/docs`.

### Expected Result

Swagger/OpenAPI documentation displays available API endpoints.

### Screenshot

TODO: Add screenshot of `/docs`.

## AT-10: Planned Agentic Routing Demo

### Objective

After the agentic routing upgrade is implemented, verify that ambiguous security-sensitive requests are routed to the LLM.

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

### Expected Result After Upgrade

The response should show that LLM routing was required and attempted.

Expected evidence fields after upgrade:

- `requires_llm`
- `llm_required`
- `llm_attempted`
- `llm_used`
- `llm_error`

### Screenshot

TODO: Add screenshot after implementation.
