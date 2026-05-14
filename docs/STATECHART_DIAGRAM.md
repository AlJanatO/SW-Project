# Statechart Diagram

## Request Monitoring Statechart

This statechart shows how a request moves through the security monitoring system.

```mermaid
stateDiagram-v2
    [*] --> RequestReceived
    RequestReceived --> SessionChecked
    SessionChecked --> RateLimitChecked

    RateLimitChecked --> RateLimitResponse: request limit exceeded
    RateLimitResponse --> RequestLogged
    RequestLogged --> [*]

    RateLimitChecked --> RequestBodyRead: request allowed
    RequestBodyRead --> PayloadInspected
    PayloadInspected --> RouteHandlerRuns
    RouteHandlerRuns --> ResponseCaptured
    ResponseCaptured --> RequestLogged
    RequestLogged --> [*]
```

## Analyze Endpoint Statechart

```mermaid
stateDiagram-v2
    [*] --> AnalyzePayloadSubmitted
    AnalyzePayloadSubmitted --> RequestValidated

    RequestValidated --> ValidationError: invalid path or method
    ValidationError --> [*]

    RequestValidated --> LocalSecurityCheck: valid request
    LocalSecurityCheck --> RequestStored
    RequestStored --> ContextRetrieved
    ContextRetrieved --> LLMAttempted

    LLMAttempted --> LLMClassification: provider succeeds
    LLMAttempted --> LocalFallback: provider unavailable

    LLMClassification --> AnalysisReturned
    LocalFallback --> AnalysisReturned
    AnalysisReturned --> [*]
```

## Agentic Routing Extension Statechart

```mermaid
stateDiagram-v2
    [*] --> RequestAnalyzed
    RequestAnalyzed --> Safe: no suspicious signal
    RequestAnalyzed --> Attack: clear attack signal
    RequestAnalyzed --> Ambiguous: security-sensitive but unclear

    Safe --> ResultLogged
    Attack --> ResultLogged
    Ambiguous --> LLMReview

    LLMReview --> LLMDecision: LLM succeeds
    LLMReview --> RouterFallback: LLM fails

    LLMDecision --> ResultLogged
    RouterFallback --> ResultLogged
    ResultLogged --> [*]
```
