# PROMPT B: AGENTIC ROUTING UPGRADE

## Phase

Security analysis improvement.

## Purpose

Upgrade the request analysis flow so the system uses local specialized detection for clear cases and reserves LLM reasoning for ambiguous requests.

## Feature Goal

Replace a single string-only detection result with a structured routing decision.

## Routing Decision Fields

The upgraded routing result should include:

- `classification`
- `attack_type`
- `anomaly_type`
- `confidence`
- `severity`
- `source`
- `reason`
- `requires_llm`

## Expected Behavior

| Request Type | Expected Route |
|---|---|
| Normal login | safe local decision |
| SQL injection | specialized classifier |
| XSS | specialized classifier |
| path traversal | specialized classifier |
| command injection | specialized classifier |
| large payload | suspicious review |
| token or credential ambiguity | LLM route |

## Files To Change

- `security_system/security.py`
- `security_system/services.py`
- `security_system/llm.py`
- `security_system/test_security.py`

Middleware should only change if the request logging path needs to avoid duplicate or heavy analysis.

## Files Not To Change

- `.env`
- database credentials
- unrelated UI files
- vulnerable simulation behavior
- Git history outside manual commits

## Verification Steps

Run:

```bash
python -m pytest test_security.py -v
```

Manual checks:

1. Normal request returns safe/normal.
2. SQL injection returns attack/SQL Injection.
3. Ambiguous token request sets LLM routing requirement.

## Completion Criteria

- [ ] Structured routing decision exists.
- [ ] High-confidence attacks do not require LLM.
- [ ] Normal traffic does not require LLM.
- [ ] Ambiguous cases require LLM.
- [ ] Tests pass.
- [ ] Diff reviewed before commit.

## Next Prompt

`PROMPT-C-LLM-EVIDENCE.md`
