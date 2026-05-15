# SW-Project

## Brief Description

This project is a FastAPI and PostgreSQL security monitoring system. It demonstrates how a backend can inspect request data, detect common attack patterns, record monitored events, and show the results through a browser-based demo dashboard.

The current implementation includes:

- FastAPI API routes and HTML pages.
- PostgreSQL storage for sessions, monitored requests, and detected anomalies.
- Middleware-based session tracking, rate limiting, and request inspection.
- Rule-based detection for SQL Injection, XSS, Path Traversal, Command Injection, Recursive API Abuse, and Flood-style payloads.
- A defense response for analyzed requests, including action, severity, rule, reason, and recommendation.
- A demo analyze page with rotating preset payload examples.
- A live dashboard with recent requests, recent anomalies, top IPs, and an event timeline.
- Optional LLM/RAG analysis when LLM environment variables are configured.

## Main Demo Pages

- `/` opens the landing page.
- `/analyze` opens the preset request conveyor-belt demo.
- `/dashboard` opens the live monitoring dashboard.
- `/api/health` opens the system health check.
- `/docs` opens the Swagger documentation wrapper.
- `/api/query/logs` opens the request-log view backed by the `requests` table.

## Current Architecture

```text
Browser pages and API clients
        ↓
FastAPI routes in main.py and api.py
        ↓
SecurityMiddleware for session, rate limit, and monitoring checks
        ↓
services.py for request recording, analysis, and dashboard metrics
        ↓
security.py for anomaly detection and defense response mapping
        ↓
PostgreSQL tables: sessions, requests, anomalies
```

## Database Tables

- `sessions`: tracks session ID, IP address, user agent, request count, and anomaly count.
- `requests`: stores monitored request events and powers the request-log and timeline views.
- `anomalies`: stores abnormal events with severity and explanation.

The old duplicate `logs` table is not part of the current schema. Request-log screens use the `requests` table.

## Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a local `.env` file using `.env.example` as a guide.

Required database values:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Optional LLM values:

```text
LLM_API_URL
LLM_API_KEY
LLM_MODEL
```

Optional vulnerable simulation setting:

```text
ENABLE_VULN_SIMULATION=true
```

## Run The Application

From `security_system/`:

```bash
python -m uvicorn main:app --reload
```

From the project root:

```bash
python -m uvicorn security_system.main:app --reload
```

## Run Tests

From `security_system/`:

```bash
python -m pytest test_security.py -v
```

## Recommended Demo Flow

1. Open `/api/health` to confirm the database connection.
2. Open `/dashboard` to show the current request timeline.
3. Open `/analyze`.
4. Press `Normal`, then `Analyze`, and show the allowed defense response.
5. Press `SQL Injection`, then `Analyze`, and show the blocked critical response.
6. Press `XSS`, `Path Traversal`, `Command Injection`, `Recursive Abuse`, or `Flood Payload` to show additional attack categories.
7. Return to `/dashboard` and click timeline dots to show stored event details.