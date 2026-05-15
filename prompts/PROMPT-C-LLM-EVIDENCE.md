# Prompt C: Optional LLM/RAG Analysis

## Requirement Area

Optional LLM-assisted threat analysis and retrieval of prior request context from PostgreSQL.

## Objective

Provide an optional LLM analysis layer that can classify and explain requests using the current payload plus relevant historical request context. The system must still work when LLM credentials are not configured.

## Implemented Behavior

- `generate_payload_embedding()` converts request payloads into deterministic local vector embeddings.
- `record_request()` stores each payload embedding in the `requests.payload_embedding` column.
- `retrieve_context()` compares the current payload embedding against stored request embeddings using cosine similarity.
- `_call_external_llm()` sends the payload and context to an external LLM provider when environment variables are configured.
- `_parse_llm_response()` extracts JSON classification and explanation from the model output.
- `analyze_with_llm()` falls back to local detection if the LLM is unavailable.

## Current Retrieval Scope

The current RAG-style retrieval uses local vector embeddings stored in PostgreSQL as `JSONB`. The implementation avoids external embedding API calls and `pgvector` installation so it remains simple to run in the course environment while still ranking prior requests by vector similarity.

## Environment Variables

- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

## Response Evidence

- `classification`
- `rule_classification`
- `context`
- `context.retrieval_method`
- `context.embedding_dimensions`
- `context.similar_events[*].similarity`
- `llm_result`
- `explanation`

## Files Involved

- `security_system/llm.py`
- `security_system/services.py`
- `security_system/test_security.py`

## Acceptance Criteria

- LLM parsing handles valid JSON.
- LLM parsing handles markdown-wrapped JSON.
- Plain text output falls back to safe/suspicious/attack keyword handling.
- Missing credentials do not crash the application.
- `/api/analyze` still returns a complete response when the LLM is unavailable.
- Similar request context is ranked by local vector cosine similarity.

## Vector-Based Similarity Search

The implemented retrieval path:

- generates a normalized embedding from payload tokens
- stores the embedding with the request record
- loads recent embedded request records
- ranks them by cosine similarity
- returns the top eight events as LLM context

A future production version could replace the local deterministic embedding with provider embeddings and `pgvector` nearest-neighbor queries.

## Verification Payload

```json
{
  "path": "/review",
  "method": "POST",
  "payload": {
    "message": "please review this admin token behavior"
  }
}
```
