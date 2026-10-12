"""Thread-safe token-bucket rate limiter for protecting ECS service tasks."""

import threading
import time
from collections import defaultdict


class TokenBucketRateLimiter:
    """In-memory token bucket rate limiter per client IP address."""

    def __init__(self, rate: float = 100.0, capacity: float = 200.0):
        self.rate = float(rate)  # tokens added per second
        self.capacity = float(capacity)  # max bucket burst capacity
        self.buckets = defaultdict(lambda: {"tokens": self.capacity, "last_updated": time.time()})
        self._lock = threading.Lock()

    def is_allowed(self, client_id: str, tokens_needed: float = 1.0) -> bool:
        """Check if client is allowed to consume tokens."""
        now = time.time()
        with self._lock:
            bucket = self.buckets[client_id]
            elapsed = now - bucket["last_updated"]
            bucket["last_updated"] = now
            # Replenish tokens based on elapsed time
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.rate)

            if bucket["tokens"] >= tokens_needed:
                bucket["tokens"] -= tokens_needed
                return True
            return False

    def reset(self):
        """Reset all buckets (useful for test isolation)."""
        with self._lock:
            self.buckets.clear()
