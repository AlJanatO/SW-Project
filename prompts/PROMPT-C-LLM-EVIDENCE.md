# PROMPT C: LLM EVIDENCE FIELDS

## Phase

LLM auditability and verification.

## Purpose

Make the API response clearly show whether LLM reasoning was required, attempted, successfully used, or unavailable.

## Feature Goal

Add explicit LLM evidence fields to the analysis response.

## Fields To Add

- `llm_required`
- `llm_attempted`
- `llm_used`
- `llm_error`

## Why This Matters

The project uses an LLM as part of the security analysis path. The response should make that behavior visible for testing, debugging, and screenshots.

Without these fields, an ambiguous request may show `llm_result: null`, but it is not obvious whether the LLM was skipped, unavailable, rate-limited, or not configured.

## Files To Change

- `security_system/llm.py`
- `security_system/test_security.py`

## Verification Tests

Add or update tests for:

1. Safe request does not require or attempt LLM.
2. Suspicious request attempts LLM and records an error when the call fails.
3. Suspicious request uses LLM result when the call succeeds.

## Manual Demo Payload

```json
{
  "path": "/review",
  "method": "POST",
  "payload": {
    "message": "please review this admin token behavior"
  }
}
```

## Expected Evidence

If the LLM provider is unavailable or rate-limited:

```json
{
  "llm_required": true,
  "llm_attempted": true,
  "llm_used": false,
  "llm_error": "..."
}
```

If the LLM succeeds:

```json
{
  "llm_required": true,
  "llm_attempted": true,
  "llm_used": true,
  "llm_error": null
}
```

## Completion Criteria

- [ ] LLM evidence fields are present.
- [ ] LLM failure does not crash the app.
- [ ] Tests cover success and failure paths.
- [ ] Manual screenshot can show LLM evidence.

## Next Prompt

`PROMPT-D-DOCUMENTATION.md`
