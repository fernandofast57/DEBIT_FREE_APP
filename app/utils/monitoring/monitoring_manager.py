import logging
import time
import psutil
from datetime import datetime
from typing import Dict, Any, List, Set
from functools import wraps

logger = logging.getLogger(__name__)

class MonitoringManager:
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': [],
            'response_times': [],
            'error_counts': {},
            'endpoint_usage': {},
            'active_users': set()
        }

    def collect_metrics(self) -> Dict[str, Any]:
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv
            }
            
            self._update_metrics(metrics)
            self._check_thresholds(metrics)
            return metrics
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            return {}

    def _update_metrics(self, metrics: Dict[str, Any]):
        self.metrics['cpu_usage'].append(metrics['cpu_percent'])
        self.metrics['memory_usage'].append(metrics['memory_percent'])
        self.metrics['disk_usage'].append(metrics['disk_percent'])

    def _check_thresholds(self, metrics: Dict[str, Any]):
        if metrics['cpu_percent'] > 80:
            logger.warning(f"High CPU usage: {metrics['cpu_percent']}%")
        if metrics['memory_percent'] > 85:
            logger.warning(f"High memory usage: {metrics['memory_percent']}%")

    def log_request(self, endpoint: str) -> None:
        if endpoint not in self.metrics['endpoint_usage']:
            self.metrics['endpoint_usage'][endpoint] = 0
        self.metrics['endpoint_usage'][endpoint] += 1

    def log_error(self, error_type: str) -> None:
        if error_type not in self.metrics['error_counts']:
            self.metrics['error_counts'][error_type] = 0
        self.metrics['error_counts'][error_type] += 1

    def log_response_time(self, time: float) -> None:
        self.metrics['response_times'].append(time)

    def get_average_response_time(self) -> float:
        if not self.metrics['response_times']:
            return 0.0
        return sum(self.metrics['response_times']) / len(self.metrics['response_times'])

import logging
from typing import Optional
from .performance_monitor import SystemPerformanceMonitor

_performance_monitor: Optional[SystemPerformanceMonitor] = None

def get_performance_monitor() -> SystemPerformanceMonitor:
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = SystemPerformanceMonitor()
    return _performance_monitor

__all__ = ['get_performance_monitor']