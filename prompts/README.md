# Security Monitor Development Prompts

This folder contains the development prompts used to build and document the security monitoring project in phases.

Each prompt is written as a small project checkpoint with:

- the feature goal
- the files involved
- verification steps
- the reason for the change
- the next checkpoint

## Prompt Sequence

| Prompt | Title | Purpose |
|---|---|---|
| `PROMPT-A-BASELINE-SECURITY.md` | Baseline Security System | Documents the existing FastAPI, PostgreSQL, middleware, and detection flow |
| `PROMPT-B-AGENTIC-ROUTING.md` | Agentic Routing Upgrade | Defines the next implementation step for specialized classifier + LLM routing |
| `PROMPT-C-LLM-EVIDENCE.md` | LLM Evidence Fields | Defines how to make LLM usage visible in responses and tests |

## Development Flow

```text
Baseline security monitor
   ↓
Agentic routing upgrade
   ↓
LLM usage evidence
   ↓
Acceptance tests and documentation updates
```

## Verification Rule

Before moving from one prompt to the next:

1. Inspect the diff.
2. Run relevant tests.
3. Check the app manually if the prompt changes behavior.
4. Commit the completed checkpoint.
5. Continue with the next prompt.

## Current Project Direction

The project starts as a working FastAPI security monitor with rule-based detection and optional LLM analysis. The next major feature is an agentic routing upgrade that uses local specialized classifiers for obvious attacks and reserves LLM calls for ambiguous security-sensitive requests.
