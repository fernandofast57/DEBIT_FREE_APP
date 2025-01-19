import time
import functools
import logging
from typing import Dict, List, Any
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'distribution': [],
            'database_operations': [],
            'transaction_processing': []
        }
        self.start_time = datetime.now()

    def track_time(self, category: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                if category not in self.metrics:
                    self.metrics[category] = []
                self.metrics[category].append(execution_time)
                return result
            return wrapper
        return decorator

    def get_metrics(self) -> Dict[str, Any]:
        return {
            category: {
                'average': sum(times) / len(times) if times else 0,
                'count': len(times),
                'total_time': sum(times) if times else 0
            }
            for category, times in self.metrics.items()
        }

performance_monitor = PerformanceMonitor()