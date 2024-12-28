
import time
import logging
from functools import wraps
from statistics import mean, median
from typing import Dict, List, Callable
import threading

class PerformanceMonitor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.metrics = {}
                cls._instance.thresholds = {
                    'api_response': 200,  # ms
                    'database_query': 100,  # ms
                    'blockchain_operation': 1000  # ms
                }
            return cls._instance
    
    def track_time(self, category: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                if category not in self.metrics:
                    self.metrics[category] = []
                self.metrics[category].append(execution_time)
                
                if execution_time > self.thresholds.get(category, 1000):
                    logging.warning(f"Performance threshold exceeded for {category}: {execution_time}ms")
                
                return result
            return wrapper
        return decorator
    
    def get_metrics(self, category: str) -> Dict:
        if category not in self.metrics:
            return {}
        
        times = self.metrics[category]
        return {
            'count': len(times),
            'average': mean(times),
            'median': median(times),
            'min': min(times),
            'max': max(times)
        }
    
    def reset_metrics(self):
        self.metrics.clear()

performance_monitor = PerformanceMonitor()
