import time
import logging
import functools
from typing import Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceProfiler:
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}

    def profile(self, operation_name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.perf_counter() - start_time
                    self._record_profile(operation_name, execution_time, True)
                    return result
                except Exception as e:
                    execution_time = time.perf_counter() - start_time
                    self._record_profile(operation_name, execution_time, False)
                    raise e
            return wrapper
        return decorator

    def _record_profile(self, operation: str, duration: float, success: bool) -> None:
        if operation not in self.profiles:
            self.profiles[operation] = {
                'count': 0,
                'total_time': 0.0,
                'failures': 0,
                'last_execution': None
            }

        profile = self.profiles[operation]
        profile['count'] += 1
        profile['total_time'] += duration
        if not success:
            profile['failures'] += 1
        profile['last_execution'] = datetime.utcnow().isoformat()