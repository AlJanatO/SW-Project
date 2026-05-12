QUERIES = {
    "logs": "SELECT id, created_at, ip, endpoint, method, status_code, anomaly_type FROM requests ORDER BY id DESC LIMIT 25",
}


def get_query(name: str):
    return QUERIES.get(name)