"""Production smoke-test suite for deployed environments over HTTP.

Executed in CI/CD pipeline post-deployment to staging (or dev) before promotion
gates are unlocked. Validates functional correctness, probe endpoints, Prometheus
telemetry exposition, and latency SLAs.

Usage:
    python integration_test.py http://<alb-dns-name> [--max-latency-ms 500]
"""

import json
import sys
import time
import urllib.error
import urllib.request

MAX_LATENCY_THRESHOLD_SEC = 0.500  # 500ms SLA for staging smoke checks


def verify_endpoint(
    base_url: str,
    path: str,
    expected_status: int = 200,
    expected_substring: str = None,
    retries: int = 12,
    initial_delay: float = 3.0,
    max_latency_sec: float = MAX_LATENCY_THRESHOLD_SEC
) -> bool:
    """Verifies an HTTP endpoint with exponential backoff retries and latency thresholding."""
    full_url = base_url.rstrip("/") + path
    delay = initial_delay

    for attempt in range(1, retries + 1):
        try:
            start_time = time.time()
            req = urllib.request.Request(
                full_url,
                headers={"User-Agent": "CI-IntegrationTest/1.0", "X-Request-ID": f"smoke-test-{attempt}"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                elapsed_sec = time.time() - start_time
                status = resp.status
                body = resp.read().decode("utf-8")

                if status == expected_status:
                    if expected_substring and expected_substring not in body:
                        print(f"[{attempt}/{retries}] FAIL: {full_url} missing expected substring '{expected_substring}'")
                    elif elapsed_sec > max_latency_sec:
                        print(f"[{attempt}/{retries}] WARN: {full_url} exceeded latency SLA ({elapsed_sec*1000:.1f}ms > {max_latency_sec*1000:.1f}ms)")
                        # Allow retry if ALB connection pool was warming up
                    else:
                        print(f"PASS {full_url} -> HTTP {status} in {elapsed_sec*1000:.1f}ms")
                        return True
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"[{attempt}/{retries}] Pending {full_url}: {exc}")

        time.sleep(delay)
        delay = min(delay * 1.5, 15.0)  # Exponential backoff capped at 15s

    print(f"CRITICAL: {full_url} failed after {retries} attempts.")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: integration_test.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    print(f"Starting production smoke validation against: {base_url}")
    print(f"Latency SLA threshold: {MAX_LATENCY_THRESHOLD_SEC * 1000:.0f}ms\n")

    test_matrix = [
        {"path": "/health", "expected_status": 200, "expected_substring": '"status":"ok"'},
        {"path": "/livez", "expected_status": 200, "expected_substring": '"status":"alive"'},
        {"path": "/readyz", "expected_status": 200, "expected_substring": '"status":"ready"'},
        {"path": "/version", "expected_status": 200, "expected_substring": '"version"'},
        {"path": "/api/items", "expected_status": 200, "expected_substring": '"items"'},
        {"path": "/metrics", "expected_status": 200, "expected_substring": "http_requests_total"},
    ]

    all_passed = True
    for item in test_matrix:
        passed = verify_endpoint(
            base_url=base_url,
            path=item["path"],
            expected_status=item["expected_status"],
            expected_substring=item.get("expected_substring")
        )
        if not passed:
            all_passed = False

    if not all_passed:
        print("\nIntegration test suite FAILED. Aborting promotion pipeline.")
        sys.exit(1)

    print("\nAll production smoke checks and latency SLAs PASSED successfully.")


if __name__ == "__main__":
    main()
