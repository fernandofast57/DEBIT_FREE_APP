
import time
import functools
import logging
from typing import Dict, List, Any, Callable
from datetime import datetime

def monitor_performance(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result
    return wrapper

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'response_time': [],
            'database_query_times': [],
            'blockchain_operation_times': []
        }
        self.start_time = datetime.now()

    def record_metric(self, category: str, value: float) -> None:
        if category not in self.metrics:
            self.metrics[category] = []
        self.metrics[category].append(value)

    def get_average(self, category: str) -> float:
        if not self.metrics.get(category):
            return 0.0
        return sum(self.metrics[category]) / len(self.metrics[category])

    def get_metrics(self) -> Dict[str, Any]:
        return {
            category: {
                'average': self.get_average(category),
                'count': len(values),
                'latest': values[-1] if values else 0
            }
            for category, values in self.metrics.items()
        }

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'response_time': [],
            'database_query_times': [],
            'blockchain_operation_times': []
        }
        self.start_time = datetime.now()
        self._shutdown_flag = False

    def save_metrics(self) -> None:
        """Save current metrics to storage"""
        if not self._shutdown_flag:
            self._shutdown_flag = True
            metrics = self.get_metrics()
            logging.info(f"Saving metrics before shutdown: {metrics}")

    def track_time(self, category: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                self.record_metric(category, execution_time)
                return result
            return wrapper
        return decorator

# Create the singleton instance
performance_monitor = PerformanceMonitor()
