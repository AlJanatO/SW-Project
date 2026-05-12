from fastapi import APIRouter, Query
from db import get_connection

router = APIRouter()


@router.get("/")
def vulnerable_root():
    return {
        "status": "enabled",
        "warning": "Vulnerable simulation routes are active.",
        "routes": [
            "/vuln/sql",
            "/vuln/recursive",
            "/vuln/stress"
        ]
    }


@router.get("/sql")
def vulnerable_sql(query: str = Query(..., description="Raw SQL to execute (intentionally unsafe).")):
    conn = get_connection()
    cur = conn.cursor()

    # Intentionally unsafe: direct string execution for SQL injection simulation.
    cur.execute(query)

    try:
        rows = cur.fetchall()
    except Exception:
        rows = []

    conn.commit()
    cur.close()
    conn.close()

    return {
        "mode": "intentionally_vulnerable",
        "executed_query": query,
        "rows": rows
    }


@router.get("/recursive")
def vulnerable_recursive(depth: int = 0, limit: int = 25):
    # Intentionally recursive simulation route.
    if depth >= limit:
        return {"depth": depth, "status": "completed"}

    return vulnerable_recursive(depth=depth + 1, limit=limit)


@router.get("/stress")
def vulnerable_stress(size: int = 250000):
    # Intentionally expensive operation to simulate resource pressure.
    data = ["X" * 512 for _ in range(size)]
    return {
        "allocated_items": len(data),
        "status": "stress simulation complete"
    }
