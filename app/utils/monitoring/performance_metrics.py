
from prometheus_client import Counter, Histogram
import time
from functools import wraps
from typing import Callable

db_operation_duration = Histogram(
    'db_operation_duration_seconds',
    'Time spent in database operations',
    ['operation_type']
)

db_errors = Counter(
    'db_errors_total',

concurrent_users = Gauge(
    'concurrent_users',
    'Number of concurrent users'
)

memory_usage = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes'
)

cache_hits = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

    'Total number of database errors',
    ['error_type']
)

def monitor_db_operation(operation_type: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                db_errors.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                db_operation_duration.labels(operation_type=operation_type).observe(duration)
        return wrapper
    return decorator
