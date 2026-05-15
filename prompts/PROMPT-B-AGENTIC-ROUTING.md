# Prompt B: Local Detection and Defense Response

## Requirement Area

Rule-based anomaly detection, attack classification, and professor-friendly defense response output.

## Objective

Implement local security checks that identify common backend attack patterns and return an actionable defense response for each analyzed request.

## Implemented Detection Categories

- SQL Injection Attempt
- XSS Attempt
- Path Traversal Attempt
- Command Injection Attempt
- Recursive API Abuse
- Possible Flood Attack
- Rate Limit Exceeded
- Normal

## Defense Response Fields

- `action`
- `severity`
- `rule`
- `reason`
- `recommendation`

## Expected Demo Behavior

| Request Type | Expected Result |
|---|---|
| Normal login | allowed, low severity |
| SQL injection | blocked, critical severity |
| XSS | blocked, high severity |
| Path traversal | blocked, high severity |
| Command injection | blocked, critical severity |
| Recursive API abuse | blocked, medium severity |
| Oversized payload | blocked, medium severity |

## Files Involved

- `security_system/security.py`
- `security_system/services.py`
- `security_system/models.py`
- `security_system/test_security.py`

## Acceptance Criteria

- Each attack type returns a clear anomaly label.
- Each anomaly label maps to a defense response.
- `/api/analyze` includes the defense object.
- The analyze page renders defense details for demo explanation.
- Tests cover normal and malicious payloads.

## Verification Evidence

```bash
python -m pytest test_security.py -v
```

