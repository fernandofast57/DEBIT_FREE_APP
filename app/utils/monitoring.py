
import logging
import time
from functools import wraps
from flask import request
from typing import Dict, Any, Optional
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.logger = logging.getLogger('system_monitor')
        self.metrics: Dict[str, Any] = {
            'response_times': [],
            'error_counts': {},
            'endpoint_usage': {},
            'active_users': set()
        }

    def log_request(self, endpoint: Optional[str] = None) -> None:
        endpoint_name = endpoint or getattr(request, 'endpoint', 'unknown')
        self.metrics['endpoint_usage'][endpoint_name] = self.metrics['endpoint_usage'].get(endpoint_name, 0) + 1

    def log_error(self, error_type: str) -> None:
        self.metrics['error_counts'][error_type] = self.metrics['error_counts'].get(error_type, 0) + 1

    def log_response_time(self, duration: float) -> None:
        self.metrics['response_times'].append(duration)

    def get_average_response_time(self) -> float:
        times = self.metrics['response_times']
        return sum(times) / len(times) if times else 0.0

    def get_metrics(self) -> Dict[str, Any]:
        return {
            'avg_response_time': self.get_average_response_time(),
            'error_counts': self.metrics['error_counts'],
            'endpoint_usage': self.metrics['endpoint_usage'],
            'active_users_count': len(self.metrics['active_users'])
        }

system_monitor = SystemMonitor()

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            system_monitor.log_response_time(duration)
            system_monitor.log_request(request.endpoint)
            return result
        except Exception as e:
            system_monitor.log_error(type(e).__name__)
            raise
    return decorated_function
