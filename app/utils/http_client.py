"""Resilient HTTP client with circuit breaker, exponential backoff, and full jitter."""

import enum
import logging
import random
import time
from typing import Callable, Any, Optional

logger = logging.getLogger("resilience.http")


class CircuitState(enum.Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class ResilientCircuitBreaker:
    """Circuit breaker pattern preventing catastrophic cascade failures during outages."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error("Circuit breaker tripped to OPEN state due to consecutive errors.")

    def can_execute(self) -> bool:
        """Evaluate if downstream request can be executed."""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if (time.time() - self.last_state_change) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state to test downstream health.")
                return True
            return False
        # HALF_OPEN
        return True


def execute_with_retry(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    circuit_breaker: Optional[ResilientCircuitBreaker] = None
) -> Any:
    """Execute callable with decorrelated exponential backoff and full jitter."""
    if circuit_breaker and not circuit_breaker.can_execute():
        raise RuntimeError("Circuit breaker is OPEN. Downstream service unavailable.")

    attempt = 0
    while True:
        try:
            result = func()
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
        except Exception as err:
            attempt += 1
            if circuit_breaker:
                circuit_breaker.record_failure()
            if attempt > max_retries:
                logger.error(f"Execution failed after {max_retries} retries: {err}")
                raise
            # Exponential backoff with full jitter
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jittered_delay = random.uniform(0, delay)
            time.sleep(jittered_delay)
