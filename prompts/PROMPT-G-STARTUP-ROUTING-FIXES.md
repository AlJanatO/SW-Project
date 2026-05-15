# Prompt G: Startup and Routing Fixes

## Requirement Area

Application startup reliability, FastAPI route organization, and UI/API separation.

## Objective

Resolve startup and routing problems that prevented the FastAPI application from loading consistently and prevented the browser UI from displaying the intended navigation page.

## Project Context

The application is a FastAPI security monitoring system with both API endpoints and browser-facing HTML pages. The system must expose API routes for analysis and query execution while also serving a usable dashboard and demo interface.

## Issues Addressed

### ASGI Startup Failure

The application failed to load with an error indicating that `app` could not be found in `main.py`. The underlying issue was an import-time failure caused by API code importing a missing service function before the FastAPI application finished loading.

### Route Collision

The browser home page did not show the expected navigation interface because both the main UI module and API router exposed root-level routes. The API router needed to be namespaced to prevent it from overriding the HTML UI route.

## Implementation Scope

The fix required the backend to:

- expose `execute_query()` through the service layer
- keep query execution centralized through named queries
- mount API routes under `/api`
- preserve `/` for the HTML landing page
- update navigation links to point to the correct API paths

## Files Involved

- `security_system/main.py`
- `security_system/api.py`
- `security_system/services.py`
- `security_system/queries.py`
- `security_system/ui.py`

## Acceptance Criteria

- The application starts successfully with Uvicorn.
- The root path `/` displays the HTML landing page.
- API endpoints are available under `/api`.
- Query endpoints return data through named query execution.
- UI navigation links point to valid routes.
- Route collisions do not prevent the browser interface from rendering.

## Verification Evidence

Recommended verification commands and pages:

```bash
python -m uvicorn main:app --reload
```

Manual checks:

- `/`
- `/analyze`
- `/dashboard`
- `/api/health`
- `/api/query/logs`
- `/docs`

## Completion Criteria

The startup and routing fixes are complete when the backend loads without import errors, the UI pages render correctly, and the API routes remain accessible under the `/api` namespace.
