# Prompt A: Core Security Monitoring Architecture

## Requirement Area

Baseline FastAPI application, MVC-style organization, API routing, and security monitoring flow.

## Objective

Implement a web-based security monitoring system that accepts HTTP traffic, inspects request payloads, stores monitored activity in PostgreSQL, and exposes both API and browser-facing views for demonstration.

## Implementation Scope

- `security_system/main.py`
- `security_system/api.py`
- `security_system/middleware.py`
- `security_system/services.py`
- `security_system/security.py`
- `security_system/db.py`
- `security_system/models.py`
- `security_system/ui.py`

## MVC Mapping

| Layer | Project Files | Responsibility |
|---|---|---|
| View | `main.py`, `ui.py` | Browser pages, navigation, analyze form, dashboard display |
| Controller | `api.py`, `main.py` | FastAPI route handlers and request routing |
| Model | `models.py`, PostgreSQL schema | Pydantic validation and database tables |
| Service | `services.py` | Request recording, analysis, metrics, query execution |
| Security | `middleware.py`, `security.py`, `llm.py` | Session tracking, rate limits, anomaly detection, optional LLM analysis |

## Expected Behavior

- Start as a FastAPI application.
- Register UI routes and API routes without route collision.
- Track client sessions.
- Apply rate limiting.
- Inspect request payloads.
- Store monitored request records.
- Store anomaly records when attacks are detected.
- Expose `/api/health`, `/api/analyze`, `/api/dashboard/metrics`, `/dashboard`, `/analyze`, and `/docs`.

## Acceptance Criteria

- The root page loads as HTML.
- API routes are namespaced under `/api`.
- The health page confirms database connectivity.
- Requests can be analyzed through `/api/analyze`.
- Dashboard metrics can be retrieved through `/api/dashboard/metrics`.
- Automated tests pass.

## Verification Evidence

```bash
python -m pytest test_security.py -v
python -m uvicorn main:app --reload
```
