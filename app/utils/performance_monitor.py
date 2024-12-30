
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

performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start_time) * 1000
        performance_monitor.track_time('api_response')(lambda: None)()
        return result
    return wrapper
import time
import logging
from functools import wraps
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'api_response_times': {},
            'database_query_times': {},
            'blockchain_operation_times': {}
        }

    def track_performance(self, category: str):
        def decorator(func):
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
