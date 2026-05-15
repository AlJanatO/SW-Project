# System Structure

## Overview

The system is a FastAPI web application backed by PostgreSQL. It monitors API activity, records request history, detects common attack patterns, and optionally uses an LLM with retrieved log context to explain or classify requests.

## Main Project Areas

```text
SW-Project-1/
├── security_system/        # FastAPI application and tests
├── prompts/                # Development prompts used for implementation planning
├── docs/                   # UML, statechart, and flow diagrams
├── APIdoc/                 # Static API reference
├── database/               # PostgreSQL schema reference
├── sample_data/            # Demo request payloads
├── diagrams/               # Editable PlantUML diagram sources
├── anomalies/              # Supporting anomaly-related files/data
├── README.md               # Main project instructions
├── project_srs.txt         # Software requirements specification
├── proj_description.txt    # Brief project description
├── ACCEPTANCE_TESTS.md     # Manual acceptance test plan
├── ARCHITECTURE_SUMMARY.md # Architecture explanation
└── PROJECT_DELIVERY_SUMMARY.md
```

## Application Code Structure

```text
security_system/
├── main.py              # FastAPI app setup and route registration
├── api.py               # API endpoints for analysis, health, query, and dashboard metrics
├── middleware.py        # Session tracking, rate limiting, request inspection, and logging
├── services.py          # Business logic for sessions, requests, analysis, and dashboard data
├── security.py          # Local anomaly detection and rate limit helper
├── llm.py               # LLM context retrieval, API call, parser, and fallback behavior
├── db.py                # PostgreSQL query execution helper
├── models.py            # Pydantic request/response models
├── queries.py           # Registered database queries
├── ui.py                # HTML layout and browser pages
└── test_security.py     # Unit and integration tests
```

## Runtime Flow

1. A client sends a request to the FastAPI application.
2. Middleware checks whether the path should be logged so page loads do not create duplicate dashboard data.
3. Middleware checks the session and rate limit for logged API/simulation traffic.
4. API routes call the service layer.
5. The service layer records each analyzed request once in PostgreSQL.
6. Local detection returns an anomaly label and defense response.
7. `/api/analyze` also calls the LLM analysis path.
8. The LLM path retrieves similar historical events from PostgreSQL.
9. If an LLM provider is configured, the request and context are sent for classification.
10. If the LLM is unavailable, the system falls back to local detection.
11. Results are returned to the user and stored for dashboard review.

## Data Storage and Supporting Data

The project uses PostgreSQL instead of local CSV files. The main supporting data for the system is stored in database tables used by the service layer.

### Runtime Data

- **Request logs**: records endpoint, method, payload, status code, IP/session context, and detected anomaly type.
- **Anomaly records**: stores requests that were classified as abnormal or suspicious.
- **Session records**: tracks active sessions, IP addresses, and user agents.
- **Timeline data**: built from the `requests` table using each record's `created_at` timestamp.

### LLM Context Data

`llm.py` retrieves similar previous request records from PostgreSQL and uses them as context for LLM analysis. This is the project equivalent of a supporting data layer: previous requests become evidence for future request classification.

### Environment Configuration

The app expects configuration values in `.env`, which is ignored by Git. Important variables include:

- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `ENABLE_VULN_SIMULATION`

## Key Design Choices

- **FastAPI** provides API routing and generated Swagger documentation.
- **Pydantic** validates request models.
- **PostgreSQL** stores requests, sessions, and anomalies.
- **Middleware** provides monitoring for every HTTP request.
- **Local detection** provides deterministic security checks.
- **Defense response building** explains what the system would block, why, and how to fix it.
- **LLM analysis** adds optional contextual reasoning when configured.
- **Pytest** verifies detection, parsing, models, queries, and endpoints.

## Extension Points

The easiest places to add new features are:

- `security.py` for new local detection rules.
- `llm.py` for improved LLM prompts and parsing.
- `services.py` for new business logic.
- `api.py` for new endpoints.
- `ui.py` for new browser pages.
- `test_security.py` for regression tests.

## Current Demo Focus

The current demo focuses on preset request analysis, defense response generation, request-log review, health checking, and dashboard timeline visualization.
