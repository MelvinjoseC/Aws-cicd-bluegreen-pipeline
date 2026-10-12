"""Automated OpenAPI contract conformance tests."""

def test_openapi_contract_conformance(client):
    """Assert live endpoints match status codes documented in OpenAPI 3.1 spec."""
    endpoints = [
        ("/", 200),
        ("/health", 200),
        ("/livez", 200),
        ("/readyz", 200),
        ("/health/diagnostic", 200),
        ("/api/items", 200),
    ]
    for path, expected_status in endpoints:
        response = client.get(path)
        assert response.status_code == expected_status, f"Contract mismatch on {path}"
