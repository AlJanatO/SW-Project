# PROMPT A: BASELINE SECURITY SYSTEM

## Phase

Core security monitor baseline.

## Purpose

Document and verify the existing FastAPI security monitoring behavior before adding larger features.

## Existing Files

- `security_system/main.py`
- `security_system/api.py`
- `security_system/middleware.py`
- `security_system/services.py`
- `security_system/security.py`
- `security_system/llm.py`
- `security_system/db.py`
- `security_system/models.py`
- `security_system/test_security.py`

## Existing Behavior

The baseline system supports:

- request logging
- session tracking
- rate limiting
- anomaly detection
- optional LLM analysis
- dashboard metrics
- health check output
- pytest verification

## Security Detection Categories

`detect_anomaly()` checks for:

- SQL injection
- XSS
- path traversal
- command injection
- recursive API abuse
- flood-like payloads
- normal traffic

## LLM Behavior

`analyze_with_llm()` retrieves context from previous logs and attempts an external LLM call if configured. If the LLM is unavailable, the system falls back to local detection.

## Verification Steps

Run tests from the `security_system` folder:

```bash
python -m pytest test_security.py -v
```

Run the app:

```bash
python -m uvicorn main:app --reload
```

Manual pages to check:

- `/`
- `/analyze`
- `/dashboard`
- `/api/health`
- `/docs`

## Acceptance Examples

Normal request should return normal classification.

SQL injection payload should be flagged.

Dashboard should show request and anomaly counts after activity.

## Completion Criteria

- [ ] Tests pass.
- [ ] App starts locally.
- [ ] Normal request works.
- [ ] Attack request is detected.
- [ ] Dashboard and health pages load.

## Next Prompt

`PROMPT-B-AGENTIC-ROUTING.md`
