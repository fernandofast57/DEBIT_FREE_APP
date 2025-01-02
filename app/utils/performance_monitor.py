
import time
import logging
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Callable, List

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'api_response_times': {},
            'database_query_times': {},
            'blockchain_operation_times': {},
            'transformation': {}
        }
        self.thresholds = {
            'api_response_times': 0.5,
            'database_query_times': 0.2,
            'blockchain_operation_times': 10,
            'transformation': 30
        }
        self.alerts = []

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
                    
                    if execution_time > self.thresholds.get(category, float('inf')):
                        self.alerts.append({
                            'category': category,
                            'function': func.__name__,
                            'execution_time': execution_time,
                            'threshold': self.thresholds[category],
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        logger.warning(f"Performance threshold exceeded in {category}: {func.__name__} took {execution_time:.2f}s")
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    raise
            return wrapper
        return decorator

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
        
    def get_alerts(self) -> List[Dict[str, Any]]:
        return self.alerts

    def record_metric(self, category: str, value: float) -> None:
        if category not in self.metrics:
            self.metrics[category] = []
        self.metrics[category].append(value)
        if value > self.thresholds.get(category, float('inf')):
            logger.warning(f"Performance threshold exceeded for {category}: {value}")

performance_monitor = PerformanceMonitor()
