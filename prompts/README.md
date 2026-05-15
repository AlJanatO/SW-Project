# Security Monitor Prompt Documentation

This folder documents the prompts and implementation checkpoints used to develop the FastAPI security monitoring project. The files are written as professional prompt specifications rather than chat transcripts.

Each prompt document includes:

- project context
- objective
- implementation scope
- affected files
- acceptance criteria
- verification evidence

## Prompt Index

| File | Area Documented |
|---|---|
| `PROMPT-A-BASELINE-SECURITY.md` | Core FastAPI security monitor architecture |
| `PROMPT-B-AGENTIC-ROUTING.md` | Implemented defense response and local detection routing |
| `PROMPT-C-LLM-EVIDENCE.md` | Optional LLM/RAG integration and fallback behavior |
| `PROMPT-D-DASHBOARD-DEMO.md` | Analyze page presets and dashboard timeline demo |
| `PROMPT-E-DATABASE-SCHEMA.md` | PostgreSQL schema and request/anomaly persistence |
| `PROMPT-F-TESTING-DOCUMENTATION.md` | Pytest coverage and submission documentation alignment |
| `PROMPT-G-STARTUP-ROUTING-FIXES.md` | Startup reliability, route collision resolution, and API/UI namespace separation |
| `PROMPT-H-LLM-RELIABILITY-FIXES.md` | LLM/RAG parsing, evidence reporting, and fallback behavior |

## Documentation Standard

The prompt files are intended to show a structured development process:

1. identify the project requirement
2. define the expected system behavior
3. identify the files that implement the behavior
4. describe the acceptance checks
5. connect the result to the final demo

## Current Project Scope

The current submitted system is a working security monitoring application with:

- FastAPI routes and HTML pages
- PostgreSQL persistence
- middleware-based monitoring
- rule-based anomaly detection
- defense response generation
- optional LLM/RAG analysis
- analyze-page preset payloads
- live dashboard metrics and timeline
- pytest verification
