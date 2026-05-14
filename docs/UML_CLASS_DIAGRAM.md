# UML Class Diagram

## Purpose

This diagram shows the main parts of the FastAPI security monitoring system and how they work together.

```mermaid
classDiagram
    class MainApp {
        +create FastAPI app
        +register middleware
        +include API routes
    }

    class APIRoutes {
        +root()
        +run_query(name)
        +analyze(payload, request)
        +dashboard_metrics()
        +health_check()
    }

    class SecurityMiddleware {
        +__call__(scope, receive, send)
        +manage session
        +check rate limit
        +log request
    }

    class SecurityService {
        +execute_query(name)
        +upsert_session(ip, user_agent, session_id)
        +record_request(...)
        +analyze_request(payload, session_id, ip)
        +get_dashboard_metrics()
    }

    class SecurityChecks {
        +detect_anomaly(payload)
        +rate_limit_exceeded(actor_key, max_requests, window_seconds)
    }

    class LLMService {
        +retrieve_context(payload, ip)
        +parse_llm_response(raw_text)
        +call_external_llm(context)
        +analyze_with_llm(payload, ip)
    }

    class Database {
        +run_sql(query, params)
    }

    class AnalyzeRequest {
        +path
        +method
        +payload
        +metadata
    }

    class AnalyzeResponse {
        +status
        +request_id
        +session_id
        +anomaly
        +analysis
    }

    MainApp --> APIRoutes
    MainApp --> SecurityMiddleware
    APIRoutes --> SecurityService
    SecurityMiddleware --> SecurityService
    SecurityMiddleware --> SecurityChecks
    SecurityService --> SecurityChecks
    SecurityService --> LLMService
    SecurityService --> Database
    LLMService --> Database
    APIRoutes --> AnalyzeRequest
    APIRoutes --> AnalyzeResponse
```

## Notes

- `APIRoutes` handles user/API interaction.
- `SecurityService` coordinates business logic and database writes.
- `SecurityChecks` performs local attack detection.
- `LLMService` adds optional contextual analysis.
- `Database` stores logs, sessions, and anomalies.
