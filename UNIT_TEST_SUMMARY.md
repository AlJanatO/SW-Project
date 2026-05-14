# Unit Test Summary

## Purpose

This document summarizes the automated tests included in `security_system/test_security.py`.

## Test Command

Run from the `security_system` folder:

```bash
python -m pytest test_security.py -v
```

## Test Areas

### Security Detection Tests

These tests verify that local anomaly detection identifies common attack patterns:

- SQL injection
- XSS
- path traversal
- command injection
- recursive API abuse
- flood-like payloads
- normal traffic

### Rate Limiting Tests

These tests verify that request counting works correctly for different actors and time windows:

- requests under the limit
- requests over the limit
- exact boundary at the limit
- independent actors

### LLM Parser Tests

These tests verify that LLM output parsing handles:

- valid JSON responses
- safe classifications
- invalid classification values
- markdown-wrapped JSON
- plain text attack/safe/suspicious responses

### Model Validation Tests

These tests verify Pydantic model behavior:

- valid analyze requests
- default fields
- invalid empty path
- invalid short method
- response model structure

### Query Registry Tests

These tests verify that predefined database queries can be found and unknown query names return no result.

### API Endpoint Tests

These tests verify major FastAPI endpoints:

- root page
- API root
- analyze endpoint with valid payload
- analyze endpoint with SQL injection payload
- analyze endpoint validation failure
- dashboard metrics endpoint
- health check endpoint
- query display endpoint

## Notes

Some endpoint tests depend on the application and database being available. If the database is not available, those tests are designed to skip rather than fail because the purpose is to test the API when the environment is configured.

## Evidence To Capture

Before final submission, run the test command and capture a screenshot showing the passing test summary.
