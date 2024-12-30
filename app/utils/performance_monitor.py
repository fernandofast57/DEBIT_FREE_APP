
import time
import logging
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'api_response_times': {},
            'database_query_times': {},
            'blockchain_operation_times': {},
            'transformation': {}
        }

    def track_time(self, category: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if category not in self.metrics:
                        self.metrics[category] = {}
                    
                    self.metrics[category][func.__name__] = {
                        'last_execution_time': execution_time,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    if execution_time > 1.0:  # Alert on slow operations
                        logger.warning(f"Slow {category} operation detected: {func.__name__} took {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    raise
            return wrapper
        return decorator

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics

performance_monitor = PerformanceMonitor()
