
import logging
import time
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def monitor_performance(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
    
    def get_average(self, name: str) -> float:
        return sum(self.metrics[name]) / len(self.metrics[name]) if self.metrics.get(name) else 0
