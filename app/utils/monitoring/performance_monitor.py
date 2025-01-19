
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
import time
import functools

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()

    def record_metric(self, category: str, value: float):
        if category not in self.metrics:
            self.metrics[category] = []
        self.metrics[category].append(value)
        logger.debug(f"Recorded metric {category}: {value}")

    def get_metrics(self, category: Optional[str] = None) -> Dict:
        if category:
            return {category: self.metrics.get(category, [])}
        return self.metrics

    def clear_metrics(self, category: Optional[str] = None):
        if category:
            self.metrics[category] = []
        else:
            self.metrics.clear()

    def track_time(self, category: str):
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                self.record_metric(category, execution_time)
                return result
            return wrapper
        return decorator

    def save_metrics(self):
        """Save metrics to log file"""
        for category, values in self.metrics.items():
            if values:
                avg = sum(values) / len(values)
                logger.info(f"Average {category}: {avg:.2f}")

performance_monitor = PerformanceMonitor()
