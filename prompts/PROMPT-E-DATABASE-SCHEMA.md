# Prompt E: Database Schema and Persistence

## Requirement Area

PostgreSQL schema design, request persistence, anomaly persistence, and dashboard query support.

## Objective

Maintain a database schema that matches the implemented monitoring system and avoids stale or duplicate tables. The database must support session tracking, monitored request history, anomaly records, dashboard metrics, and optional LLM context retrieval.

## Current Tables

| Table | Purpose |
|---|---|
| `sessions` | Tracks client/session activity, request counts, and anomaly counts |
| `requests` | Stores monitored request events used for request logs and dashboard timeline |
| `anomalies` | Stores detected anomalies with severity and explanation |

## Persistence Rules

- Normal monitored API/simulation requests are stored in `requests`.
- Detected abnormal requests are stored in both `requests` and `anomalies`.
- Noisy browser page loads and dashboard polling are filtered from security-event storage.
- The request-log screen is backed by the `requests` table.
- A separate duplicate `logs` table is not used in the current design.

## Files Involved

- `database/schema.sql`
- `database/README.md`
- `security_system/db.py`
- `security_system/services.py`
- `security_system/queries.py`

## Acceptance Criteria

- `ensure_schema()` creates the same runtime tables described by `database/schema.sql`.
- `record_request()` inserts into `requests`.
- Anomaly records are inserted into `anomalies`.
- `/api/query/logs` and `/api/query/request_logs` return request-log data from `requests`.
- Documentation does not describe a removed `logs` table.

## Verification Evidence

```bash
python -m pytest test_security.py -v
```

Manual checks:

- `/api/health`
- `/api/query/logs`
- `/dashboard`
