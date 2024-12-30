
import logging
import time
from functools import wraps
from typing import Callable, Any, Dict, List, Set

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

class SystemMonitor:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'error_counts': {},
            'endpoint_usage': {},
            'active_users': set()
        }
    
    def log_request(self, endpoint: str):
        if endpoint not in self.metrics['endpoint_usage']:
            self.metrics['endpoint_usage'][endpoint] = 0
        self.metrics['endpoint_usage'][endpoint] += 1
    
    def log_error(self, error_type: str):
        if error_type not in self.metrics['error_counts']:
            self.metrics['error_counts'][error_type] = 0
        self.metrics['error_counts'][error_type] += 1
    
    def log_response_time(self, time: float):
        self.metrics['response_times'].append(time)
    
    def get_average_response_time(self) -> float:
        if not self.metrics['response_times']:
            return 0.0
        return sum(self.metrics['response_times']) / len(self.metrics['response_times'])
