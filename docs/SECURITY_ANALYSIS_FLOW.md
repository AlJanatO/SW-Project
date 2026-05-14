# Security Analysis Flow

## Baseline Flow

```mermaid
flowchart TD
    A[Client submits request] --> B[FastAPI middleware]
    B --> C[Session and rate limit check]
    C --> D[Local anomaly detection]
    D --> E[Route or analyze endpoint]
    E --> F[Record request in PostgreSQL]
    F --> G[Return response]
```

## Analyze Endpoint Flow

```mermaid
flowchart TD
    A[Submit JSON to /api/analyze] --> B[Pydantic validation]
    B --> C[Local detect_anomaly]
    C --> D[Record request and anomaly]
    D --> E[Retrieve similar events from database]
    E --> F[Attempt LLM call]
    F --> G{LLM available?}
    G -->|Yes| H[Return LLM classification]
    G -->|No| I[Use local fallback]
    H --> J[Return analysis JSON]
    I --> J[Return analysis JSON]
```

## Agentic Routing Upgrade Flow

```mermaid
flowchart TD
    A[Request payload] --> B[Specialized local classifiers]
    B --> C{Clear attack?}
    C -->|Yes| D[Return attack classification]
    C -->|No| E{Looks normal?}
    E -->|Yes| F[Return safe classification]
    E -->|No| G[Mark as ambiguous]
    G --> H[Route to LLM]
    H --> I{LLM result available?}
    I -->|Yes| J[Use LLM decision]
    I -->|No| K[Keep router fallback]
    D --> L[Log final result]
    F --> L[Log final result]
    J --> L[Log final result]
    K --> L[Log final result]
```

## Demo Requests

### Normal Request

```json
{
  "path": "/login",
  "method": "POST",
  "payload": {
    "username": "student",
    "password": "normal-password"
  }
}
```

### SQL Injection Request

```json
{
  "path": "/login",
  "method": "POST",
  "payload": {
    "username": "admin' OR '1'='1",
    "password": "x"
  }
}
```

### Ambiguous LLM Review Request

```json
{
  "path": "/review",
  "method": "POST",
  "payload": {
    "message": "please review this admin token behavior"
  }
}
```
