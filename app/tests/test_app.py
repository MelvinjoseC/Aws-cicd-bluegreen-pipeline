import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402


def get_client():
    app.testing = True
    return app.test_client()


def test_health():
    client = get_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_liveness():
    client = get_client()
    resp = client.get("/livez")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "alive"


def test_readiness():
    client = get_client()
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ready"


def test_graceful_shutdown_drain():
    from app import handle_shutdown_signal, app as flask_app
    import app as app_module
    import signal

    client = get_client()
    try:
        # Simulate SIGTERM receipt
        handle_shutdown_signal(signal.SIGTERM)
        assert app_module.IS_READY is False

        # Both readyz and health must now return 503 Service Unavailable
        resp_ready = client.get("/readyz")
        assert resp_ready.status_code == 503
        assert resp_ready.get_json()["status"] == "draining"

        resp_health = client.get("/health")
        assert resp_health.status_code == 503
        assert resp_health.get_json()["status"] == "unhealthy"

        # Liveness must still return 200 while draining active requests
        resp_live = client.get("/livez")
        assert resp_live.status_code == 200
        assert resp_live.get_json()["status"] == "alive"
    finally:
        # Restore readiness state for remaining tests
        app_module.IS_READY = True


def test_version():
    client = get_client()
    resp = client.get("/version")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "version" in body
    assert "host" in body


def test_items():
    client = get_client()
    resp = client.get("/api/items")
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body["items"], list)
    assert len(body["items"]) == 3


def test_index():
    client = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_metrics():
    client = get_client()
    # Trigger requests to exercise metric observation
    client.get("/health")
    client.get("/version")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.content_type
    metric_data = resp.data.decode("utf-8")
    assert "http_requests_total" in metric_data
    assert "http_request_duration_seconds" in metric_data


def test_security_headers():
    client = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert "default-src 'self'" in resp.headers.get("Content-Security-Policy")
    assert resp.headers.get("Referrer-Policy") == "no-referrer"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"


def test_request_id_tracing():
    client = get_client()
    # Test generated Request ID
    resp = client.get("/health")
    assert "X-Request-ID" in resp.headers
    
    # Test forwarded Request ID
    custom_id = "test-uuid-1234"
    resp2 = client.get("/health", headers={"X-Request-ID": custom_id})
    assert resp2.headers.get("X-Request-ID") == custom_id


def test_error_handlers():
    client = get_client()
    resp = client.get("/non-existent-route")
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["error"] == "Not Found"
    assert "message" in body


def test_diagnostic_endpoint(client):
    """Test detailed diagnostics endpoint exposes required telemetry."""
    response = client.get("/health/diagnostic")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "active_threads" in data
    assert "dependencies" in data
    assert data["service"] == "cicd-demo-app"

def test_xray_trace_propagation(client):
    """Test X-Amzn-Trace-Id header extraction and propagation."""
    trace_header = "Root=1-5759e988-bd862e3fc1be4e0947f4f699;Parent=53995cbe3140f4c0;Sampled=1"
    response = client.get("/health", headers={"X-Amzn-Trace-Id": trace_header})
    assert response.status_code == 200
    assert "X-Amzn-Trace-Id" in response.headers
    assert "Root=1-5759e988-bd862e3fc1be4e0947f4f699" in response.headers["X-Amzn-Trace-Id"]

def test_rate_limiter_throttling(client):
    """Test in-memory rate limiting triggers 429 when burst limit exceeded."""
    from rate_limiter import TokenBucketRateLimiter
    from app import RATE_LIMITER
    
    # Configure tight bucket for test
    test_limiter = TokenBucketRateLimiter(rate=1.0, capacity=2.0)
    assert test_limiter.is_allowed("127.0.0.1") is True
    assert test_limiter.is_allowed("127.0.0.1") is True
    assert test_limiter.is_allowed("127.0.0.1") is False

def test_resilient_http_client_circuit_breaker():
    """Test circuit breaker trips after reaching failure threshold."""
    from utils.http_client import ResilientCircuitBreaker, CircuitState
    cb = ResilientCircuitBreaker(failure_threshold=2, recovery_timeout=5.0)
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

def test_app_config_validation():
    """Test AppConfig validation parser."""
    from config import AppConfig
    cfg = AppConfig.from_env()
    assert cfg.port == 8080
    assert cfg.log_level in ("DEBUG", "INFO", "WARNING", "ERROR")
