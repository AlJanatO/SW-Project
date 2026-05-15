# Database Reference

## Purpose

This folder documents the PostgreSQL schema used by the FastAPI security monitoring system.

## Schema Source

The application creates its tables at startup through `security_system/db.py` using `ensure_schema()`.

## File

- `schema.sql`: SQL version of the same tables created by `ensure_schema()`.

## Tables

### `sessions`

Tracks session ID, IP address, user agent, first seen time, last seen time, request count, and anomaly count.

### `requests`

Stores monitored requests with endpoint, method, payload, HTTP status code, anomaly label, IP address, session ID, analysis source, LLM usage flag, and creation time. `session_id` references `sessions(session_id)`.

### `anomalies`

Stores detected abnormal requests with severity, action, rule, explanation, and recommendation. Each anomaly can reference a request record and its owning session.

## Relationships

- `requests.session_id` references `sessions.session_id`.
- `anomalies.session_id` references `sessions.session_id`.
- `anomalies.request_id` references `requests.id`.

## Indexes

The schema includes indexes for dashboard and request-log queries:

- request session lookup
- request creation-time ordering
- request anomaly filtering
- request analysis-source filtering
- anomaly session lookup
- anomaly creation-time ordering
- anomaly severity filtering
- anomaly type filtering

## How This Supports LLM/RAG

`security_system/llm.py` reads previous request records from the `requests` table to provide context for optional LLM analysis.
