
import time
import functools
from typing import Dict, List, Any, Callable
from datetime import datetime

def monitor_performance(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        execution_time = time.time() - start_time
        print(f"Performance monitoring: {func.__name__} took {execution_time:.2f} seconds")
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

performance_monitor = PerformanceMonitor()
