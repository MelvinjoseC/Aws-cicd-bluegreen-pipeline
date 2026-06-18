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
