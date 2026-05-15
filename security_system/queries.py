REQUEST_LOGS_QUERY = "SELECT id, created_at, ip, endpoint, method, status_code, anomaly_type, analysis_source, llm_used FROM requests ORDER BY id DESC LIMIT 25"

QUERIES = {
    "request_logs": REQUEST_LOGS_QUERY,
    "logs": REQUEST_LOGS_QUERY,
}


def get_query(name: str):
    return QUERIES.get(name)