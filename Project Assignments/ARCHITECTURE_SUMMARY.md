# Security Monitoring System - Architecture Summary

## Overview

This project is a FastAPI-based security monitoring system that records API activity, detects suspicious request patterns, and supports optional LLM-assisted threat analysis using request history stored in PostgreSQL.

The design separates the application into route handling, service logic, security analysis, middleware monitoring, database access, and test coverage. This separation makes the project easier to test, explain, and extend.

## Design Goals

1. **Separation of Concerns**: API routes, service logic, security checks, LLM analysis, and database access are kept in separate files.
2. **Security Visibility**: Requests and anomalies are stored so activity can be reviewed through dashboard metrics.
3. **Safe Demonstration**: Vulnerable behavior is simulated for learning while defensive controls remain visible.
4. **Extensibility**: The detection system can be upgraded from rule-based checks to agentic routing without rewriting the full app.
5. **Testability**: Core behavior is covered with pytest tests for detection, rate limiting, models, queries, LLM parsing, and API endpoints.

## Main Components

### FastAPI Application

`security_system/main.py` creates the FastAPI app, connects middleware, and includes application routes.

### API Routes

`security_system/api.py` provides routes for:

- system status
- query results
- request analysis
- dashboard metrics
- health checks

### Middleware

`security_system/middleware.py` handles request monitoring before and after route execution. It manages sessions, rate limiting, request body buffering, anomaly detection, and request logging.

### Service Layer

`security_system/services.py` coordinates database operations, request recording, session updates, analysis requests, and dashboard metrics.

### Security Analysis

`security_system/security.py` contains local detection logic for SQL injection, XSS, path traversal, command injection, recursive API abuse, flood-like payloads, and rate limiting.

### LLM Analysis

`security_system/llm.py` retrieves similar past events from PostgreSQL and optionally calls an external LLM provider. If the LLM is unavailable, the system falls back to local classification.

### Data Models

`security_system/models.py` defines Pydantic models for request validation and response structure.

### Tests

`security_system/test_security.py` contains unit and integration tests for the most important project behavior.

## Current Request Flow

```text
Client request
   ↓
FastAPI middleware
   ↓
Session and rate-limit check
   ↓
Payload inspection
   ↓
API route
   ↓
Service layer
   ↓
Security detection and optional LLM analysis
   ↓
PostgreSQL logging
   ↓
Response returned to client
```

## Extension Path

The next feature direction is to upgrade the request analysis path into an agentic routing design:

```text
Request
   ↓
Specialized local classifier
   ↓
Safe / Attack / Ambiguous
   ↓
Use local decision or route ambiguous case to LLM
   ↓
Return analysis with routing evidence
```

This upgrade keeps the existing architecture but makes the LLM role more selective and easier to document in tests and final submission evidence.
