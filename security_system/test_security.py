"""
Unit tests for the security monitoring system.
Run with: python -m pytest tests.py -v
Requires: pip install pytest httpx
"""
import pytest
from security import detect_anomaly, rate_limit_exceeded, REQUEST_WINDOWS


# ── detect_anomaly tests ──


class TestDetectAnomaly:
    """Tests for the rule-based anomaly detection engine."""

    # SQL Injection
    def test_sql_select_injection(self):
        payload = {"body": "SELECT * FROM users"}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    def test_sql_drop_injection(self):
        payload = {"body": "DROP TABLE users"}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    def test_sql_union_injection(self):
        payload = {"body": "1 UNION SELECT username, password FROM users"}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    def test_sql_or_injection(self):
        payload = {"payload": {"username": "admin' OR '1'='1"}}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    def test_sql_delete_injection(self):
        payload = {"body": "DELETE FROM sessions WHERE 1=1"}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    def test_sql_insert_injection(self):
        payload = {"body": "INSERT INTO users VALUES('hacker','pass')"}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    def test_sql_comment_injection(self):
        payload = {"body": "admin'; -- drop everything"}
        assert detect_anomaly(payload) == "SQL Injection Attempt"

    # XSS
    def test_xss_script_tag(self):
        payload = {"body": "<script>alert('xss')</script>"}
        assert detect_anomaly(payload) == "XSS Attempt"

    def test_xss_javascript_uri(self):
        payload = {"body": "javascript:alert(1)"}
        assert detect_anomaly(payload) == "XSS Attempt"

    def test_xss_onerror(self):
        payload = {"body": '<img onerror=alert(1) src=x>'}
        assert detect_anomaly(payload) == "XSS Attempt"

    def test_xss_eval(self):
        payload = {"body": "eval(document.cookie)"}
        assert detect_anomaly(payload) == "XSS Attempt"

    # Path Traversal
    def test_path_traversal_basic(self):
        payload = {"path": "/files/../../../etc/passwd"}
        assert detect_anomaly(payload) == "Path Traversal Attempt"

    def test_path_traversal_encoded(self):
        payload = {"path": "/files/..%2f..%2fetc/passwd"}
        assert detect_anomaly(payload) == "Path Traversal Attempt"

    # Command Injection
    def test_command_injection_semicolon(self):
        payload = {"body": "test; cat /etc/passwd"}
        assert detect_anomaly(payload) == "Command Injection Attempt"

    def test_command_injection_pipe(self):
        payload = {"body": "test| cat /etc/passwd"}
        assert detect_anomaly(payload) == "Command Injection Attempt"

    def test_command_injection_subshell(self):
        payload = {"body": "$(whoami)"}
        assert detect_anomaly(payload) == "Command Injection Attempt"

    # Recursive API Abuse
    def test_recursive_abuse_http(self):
        payload = {"body": "http://localhost/vuln/recursive?depth=100"}
        assert detect_anomaly(payload) == "Recursive API Abuse"

    def test_recursive_abuse_https(self):
        payload = {"body": "https://example.com/vuln/recursive?depth=50"}
        assert detect_anomaly(payload) == "Recursive API Abuse"

    def test_url_without_recursive_is_normal(self):
        payload = {"body": "visit http://google.com for info"}
        assert detect_anomaly(payload) == "Normal"

    # Flood Attack
    def test_flood_attack_large_payload(self):
        payload = {"body": "A" * 2000}
        assert detect_anomaly(payload) == "Possible Flood Attack"

    # Normal traffic
    def test_normal_get_request(self):
        payload = {"method": "GET", "path": "/", "ip": "127.0.0.1"}
        assert detect_anomaly(payload) == "Normal"

    def test_normal_login(self):
        payload = {"method": "POST", "path": "/login", "payload": {"username": "admin", "password": "password123"}}
        assert detect_anomaly(payload) == "Normal"

    def test_normal_api_call(self):
        payload = {"method": "GET", "path": "/api/dashboard/metrics"}
        assert detect_anomaly(payload) == "Normal"

    def test_empty_payload(self):
        payload = {}
        assert detect_anomaly(payload) == "Normal"


# ── rate_limit_exceeded tests ──


class TestRateLimiting:
    """Tests for the rate limiting mechanism."""

    def setup_method(self):
        REQUEST_WINDOWS.clear()

    def test_under_limit_returns_false(self):
        for _ in range(5):
            result = rate_limit_exceeded("test_ip:session1", max_requests=10, window_seconds=60)
        assert result is False

    def test_over_limit_returns_true(self):
        for i in range(11):
            result = rate_limit_exceeded("test_ip:session2", max_requests=10, window_seconds=60)
        assert result is True

    def test_exactly_at_limit_returns_false(self):
        for i in range(10):
            result = rate_limit_exceeded("test_ip:session3", max_requests=10, window_seconds=60)
        assert result is False

    def test_different_actors_independent(self):
        for _ in range(11):
            rate_limit_exceeded("actor_a", max_requests=10, window_seconds=60)
        result = rate_limit_exceeded("actor_b", max_requests=10, window_seconds=60)
        assert result is False


# ── LLM response parser tests ──


class TestLLMResponseParser:
    """Tests for parsing LLM responses."""

    def test_valid_json_response(self):
        from llm import _parse_llm_response
        raw = '{"classification": "attack", "explanation": "SQL injection detected"}'
        result = _parse_llm_response(raw)
        assert result["classification"] == "attack"
        assert result["explanation"] == "SQL injection detected"

    def test_valid_json_safe(self):
        from llm import _parse_llm_response
        raw = '{"classification": "safe", "explanation": "Normal login request"}'
        result = _parse_llm_response(raw)
        assert result["classification"] == "safe"

    def test_invalid_classification_defaults_suspicious(self):
        from llm import _parse_llm_response
        raw = '{"classification": "unknown_value", "explanation": "test"}'
        result = _parse_llm_response(raw)
        assert result["classification"] == "suspicious"

    def test_markdown_wrapped_json(self):
        from llm import _parse_llm_response
        raw = '```json\n{"classification": "attack", "explanation": "bad request"}\n```'
        result = _parse_llm_response(raw)
        assert result["classification"] == "attack"

    def test_plain_text_with_attack_keyword(self):
        from llm import _parse_llm_response
        raw = "This looks like an attack based on the SQL patterns"
        result = _parse_llm_response(raw)
        assert result["classification"] == "attack"

    def test_plain_text_with_safe_keyword(self):
        from llm import _parse_llm_response
        raw = "This request appears safe and normal"
        result = _parse_llm_response(raw)
        assert result["classification"] == "safe"

    def test_plain_text_no_keywords_defaults_suspicious(self):
        from llm import _parse_llm_response
        raw = "I cannot determine the nature of this request"
        result = _parse_llm_response(raw)
        assert result["classification"] == "suspicious"


# ── Pydantic model validation tests ──


class TestModels:
    """Tests for request/response models."""

    def test_analyze_request_valid(self):
        from models import AnalyzeRequest
        req = AnalyzeRequest(path="/login", method="POST", payload={"user": "admin"})
        assert req.path == "/login"
        assert req.method == "POST"
        assert req.payload == {"user": "admin"}

    def test_analyze_request_defaults(self):
        from models import AnalyzeRequest
        req = AnalyzeRequest(path="/test", method="GET")
        assert req.payload == {}
        assert req.metadata == {}

    def test_analyze_request_rejects_empty_path(self):
        from models import AnalyzeRequest
        with pytest.raises(Exception):
            AnalyzeRequest(path="", method="GET")

    def test_analyze_request_rejects_short_method(self):
        from models import AnalyzeRequest
        with pytest.raises(Exception):
            AnalyzeRequest(path="/test", method="G")

    def test_analyze_response_model(self):
        from models import AnalyzeResponse
        resp = AnalyzeResponse(
            status="analyzed",
            request_id=1,
            session_id="abc-123",
            anomaly="Normal",
            analysis={"classification": "safe"}
        )
        assert resp.status == "analyzed"
        assert resp.anomaly == "Normal"


# ── Query registry tests ──


class TestQueries:
    """Tests for the query registry."""

    def test_logs_query_exists(self):
        from queries import get_query
        assert get_query("logs") is not None

    def test_unknown_query_returns_none(self):
        from queries import get_query
        assert get_query("nonexistent") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])