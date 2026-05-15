# Prompt D: Analyze Page and Dashboard Demo

## Requirement Area

Browser-based demonstration of request analysis, rotating preset payloads, defense review, and dashboard timeline visualization.

## Objective

Create a professor-friendly demo flow that lets a presenter load realistic JSON attack examples, submit them to the analysis endpoint, review the returned defense response, and confirm the stored activity on the live dashboard.

## Features Implemented

- Analyze page with preset payload buttons.
- Multiple rotating examples for each preset category.
- JSON editor that is populated by the selected preset.
- Defense response card showing action, severity, rule, reason, and recommendation.
- Analyst review popup with talking points for the demo.
- Dashboard summary cards for total requests and anomalies.
- Recent requests and recent anomalies panels.
- Stacked timeline chart grouped by minute.

## Timeline Visualization Requirement

The dashboard timeline must communicate traffic patterns clearly:

| Visual Element | Meaning |
|---|---|
| X axis | Minute of activity |
| Y axis | Number of monitored requests in that minute |
| Green bar section | Normal requests |
| Yellow section | Medium severity anomaly |
| Orange section | High severity anomaly |
| Red section | Critical anomaly |

Clicking a bar must show the underlying events for that minute.

## Files Involved

- `security_system/main.py`
- `security_system/services.py`
- `security_system/security.py`
- `security_system/models.py`

## Acceptance Criteria

- Preset buttons load valid JSON into the editor.
- Repeated button clicks rotate through different examples.
- The analyze result includes anomaly, defense, and analysis sections.
- The dashboard timeline uses time buckets, not array indexes.
- Dashboard metrics refresh without manually reloading the page.

## Verification Evidence

```bash
python -m pytest test_security.py -v
```

Manual demo pages:

- `/analyze`
- `/dashboard`
- `/api/dashboard/metrics`
