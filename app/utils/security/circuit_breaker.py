# app/utils/security/circuit_breaker.py
import time
import logging
from functools import wraps
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class CircuitBreaker:

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 30,
                 monitor: Optional[Any] = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.monitor = monitor
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def __call__(self, func: Callable):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time(
                ) - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF-OPEN"
                    logger.info("Circuit breaker entering HALF-OPEN state")
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    logger.info("Circuit breaker reset to CLOSED state")
                return result
            except Exception as e:
                self._handle_failure()
                raise

        return wrapper

    def _handle_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker OPEN after {self.failures} failures")

        if self.monitor:
            self.monitor.record_metrics({
                'circuit_breaker_state': self.state,
                'failures': self.failures
            })
