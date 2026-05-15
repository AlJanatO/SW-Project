# Prompt H: LLM Reliability and Fallback Fixes

## Requirement Area

Optional LLM/RAG integration, response parsing, evidence reporting, and graceful fallback behavior.

## Objective

Improve the LLM-assisted analysis path so the system can use an external LLM when configured while still returning reliable security analysis when credentials, provider quota, or provider responses are unavailable.

## Project Context

The security monitoring system uses local rule-based detection as the primary reliable classifier. Optional LLM/RAG analysis adds contextual explanation by retrieving previous request records from PostgreSQL and sending the current request plus historical context to an external LLM provider. The current retrieval method uses lightweight request-history and text matching rather than vector embeddings.

## Issues Addressed

The LLM path needed to avoid becoming dead code or an opaque failure point. The reliability work focused on four concerns:

- missing API credentials should not crash the system
- LLM responses must be parsed instead of stored only as raw text
- failed LLM calls should fall back to local classification
- LLM quota or rate-limit failures should not interrupt the analyze workflow
- the response should expose enough evidence to show whether LLM analysis was used

## Implementation Scope

The implementation required the LLM layer to:

- read `LLM_API_URL`, `LLM_API_KEY`, and `LLM_MODEL` from environment variables
- retrieve recent related request context from PostgreSQL
- call the external LLM only when credentials are available
- parse JSON or markdown-wrapped JSON responses
- fall back to keyword-based interpretation for plain text responses
- preserve rule-based classification when the LLM is unavailable
- return analysis evidence in the API response

## LLM Rate-Limit and Cost Control

The project monitors web traffic continuously, but continuous monitoring should not trigger an external LLM call for every page load, dashboard refresh, or browser movement. That would be slow, expensive, and could exceed provider quota. The final design keeps middleware monitoring local and lightweight, while the optional LLM path is used for explicit analysis workflows.

## Files Involved

- `security_system/llm.py`
- `security_system/services.py`
- `security_system/security.py`
- `security_system/test_security.py`
- `prompts/PROMPT-C-LLM-EVIDENCE.md`

## Acceptance Criteria

- Missing LLM credentials do not crash `/api/analyze`.
- Valid JSON model responses are parsed into structured output.
- Markdown-wrapped JSON model responses are parsed correctly.
- Plain text model output is interpreted safely.
- Rule-based detection remains available as a fallback path.
- Provider rate-limit errors still return a complete rule-based result.
- The API response includes evidence fields such as classification, rule classification, context, LLM result, and explanation.

## Future Work: Vector Retrieval

The current RAG context retrieval uses PostgreSQL request history and text-style matching. A stronger future version could:

- generate embeddings for request payloads
- store embeddings with `pgvector` or another vector database
- compare vector similarity instead of only using text matching
- retrieve semantically similar attacks even when exact keywords differ
- update `retrieve_context()` to pass nearest-neighbor context into the LLM prompt

This future enhancement would improve retrieval quality but is not required for the current tested submission.

## Verification Evidence

The pytest suite verifies the LLM parser and fallback behavior:

```bash
python -m pytest test_security.py -v
```

Relevant manual verification:

- submit a normal payload through `/analyze`
- submit an attack payload through `/analyze`
- inspect the `analysis` object in the response
- test once without LLM credentials to confirm fallback behavior
- test once with LLM credentials, if available, to confirm external analysis

## Completion Criteria

The LLM reliability work is complete when LLM analysis is optional, observable, and failure-tolerant. The system should never depend on the LLM provider to return a valid security response.
