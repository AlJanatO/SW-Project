# System Structure

## Overview

The system is a FastAPI web application backed by PostgreSQL. It monitors API activity, records request history, detects common attack patterns, and optionally uses an LLM with retrieved log context to explain or classify requests.

## Main Project Areas

```text
SW-Project-1/
├── security_system/        # FastAPI application and tests
├── prompts/                # Development prompts used for implementation planning
├── docs/                   # UML, statechart, and flow diagrams
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
2. Middleware checks the session and rate limit.
3. Middleware builds a request payload for monitoring.
4. API routes call the service layer.
5. The service layer records requests and calls local security analysis.
6. `/api/analyze` also calls the LLM analysis path.
7. The LLM path retrieves similar historical events from PostgreSQL.
8. If an LLM provider is configured, the request and context are sent for classification.
9. If the LLM is unavailable, the system falls back to local detection.
10. Results are returned to the user and stored for dashboard review.

## Key Design Choices

- **FastAPI** provides API routing and generated Swagger documentation.
- **Pydantic** validates request models.
- **PostgreSQL** stores requests, sessions, logs, and anomalies.
- **Middleware** provides monitoring for every HTTP request.
- **Local detection** provides deterministic security checks.
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

## Next Planned Improvement

The next improvement is an agentic routing upgrade. The goal is to use local specialized classifiers for clear attacks and reserve LLM analysis for ambiguous security-sensitive requests.
