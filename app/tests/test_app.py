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

