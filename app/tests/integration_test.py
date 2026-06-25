"""Smoke-tests a deployed environment over HTTP.

Used by the 'deploy to staging' job to confirm the freshly deployed
service is actually serving traffic before promotion to production.

Usage:
    python integration_test.py http://<staging-alb-dns-name>
"""

import sys
import time
import urllib.error
import urllib.request


def check(base_url, path, expected_status=200, retries=10, delay=5):
    full_url = base_url.rstrip("/") + path
    for attempt in range(1, retries + 1):
        try:
            resp = urllib.request.urlopen(full_url, timeout=5)
            if resp.status == expected_status:
                print(f"PASS {full_url} -> {resp.status}")
                return True
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"Attempt {attempt}/{retries} failed for {full_url}: {exc}")
        time.sleep(delay)
    print(f"FAIL {full_url} did not return {expected_status} after {retries} attempts")
    return False


def main():
    if len(sys.argv) != 2:
        print("Usage: integration_test.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    checks = [("/health", 200), ("/version", 200), ("/api/items", 200)]

    results = [check(base_url, path, status) for path, status in checks]

    if not all(results):
        sys.exit(1)

    print("All integration checks passed.")


if __name__ == "__main__":
    main()
