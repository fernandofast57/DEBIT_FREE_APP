import time
import functools
import logging
from typing import Dict, List, Any, Callable
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, alert_threshold: float = 0.1):
        self.alert_threshold = alert_threshold
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.cache_hits: Dict[str, int] = {}
            'blockchain_operation_times': [],
            'memory_usage': [],
            'cache_performance': [],
            'concurrent_users': [],
            'error_rates': []
        }
        self.cache_hits = {}
        self.start_time = datetime.now()
        self._shutdown_flag = False

    def record_metric(self, category: str, value: float) -> None:
        if category not in self.metrics:
            self.metrics[category] = []
        self.metrics[category].append(value)

    def get_average(self, category: str) -> float:
        if not self.metrics.get(category):
            return 0.0
        return sum(self.metrics[category]) / len(self.metrics[category])

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        return self.metrics

    def _init_operation_metrics(self, operation: str):
        if operation not in self.metrics:
            self.metrics[operation] = {
                'count': 0,
                'total_time': 0,
                'max': 0,
                'average': 0,
                'memory_usage': 0,
                'cache_hits': 0
            }
            self.cache_hits[operation] = 0

    def track_time(self, category: str):
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._init_operation_metrics(category)
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                self.metrics[category]['count'] += 1
                self.metrics[category]['total_time'] += execution_time
                self.metrics[category]['max'] = max(self.metrics[category]['max'], execution_time)
                self.metrics[category]['average'] = self.metrics[category]['total_time'] / self.metrics[category]['count']
                self.metrics[category]['cache_hits'] = self.cache_hits[category]
                
                return result

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._init_operation_metrics(category)
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                self.metrics[category]['count'] += 1
                self.metrics[category]['total_time'] += execution_time
                self.metrics[category]['max'] = max(self.metrics[category]['max'], execution_time)
                self.metrics[category]['average'] = self.metrics[category]['total_time'] / self.metrics[category]['count']
                self.metrics[category]['cache_hits'] = self.cache_hits[category]
                
                return result

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                self.record_metric(category, execution_time)
                return result
            return wrapper
        return decorator

    def save_metrics(self) -> None:
        if not self._shutdown_flag:
            self._shutdown_flag = True
            metrics = self.get_metrics()
            logging.info(f"Saving metrics before shutdown: {metrics}")

performance_monitor = PerformanceMonitor()