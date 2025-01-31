# app/utils/security/circuit_breaker.py
import time
import logging
from functools import wraps
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class CircuitBreaker:

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 30,
                 monitor: Optional[Any] = None):
        self.max_failures = failure_threshold
        self.recovery_interval = recovery_timeout
        self.failure_count = 0
        self.last_failure_timestamp = 0
        self.performance_monitor = monitor
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def __call__(self, func: Callable):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.circuit_state == "OPEN":
                if time.time() - self.last_failure_timestamp > self.recovery_interval:
                    self.circuit_state = "HALF-OPEN"
                    logger.info("Circuit breaker entering HALF-OPEN state")
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                if self.circuit_state == "HALF-OPEN":
                    self.circuit_state = "CLOSED"
                    self.failure_count = 0
                    logger.info("Circuit breaker reset to CLOSED state")
                return result
            except Exception as e:
                self._handle_failure()
                raise

        return wrapper

    def _handle_failure(self):
        self.failure_count += 1
        self.last_failure_timestamp = time.time()

        if self.failure_count >= self.max_failures:
            self.circuit_state = "OPEN"
            logger.warning(
                f"Circuit breaker OPEN after {self.failure_count} consecutive failures")

        if self.performance_monitor:
            self.performance_monitor.record_metrics({
                'circuit_state': self.circuit_state,
                'failure_count': self.failure_count
            })