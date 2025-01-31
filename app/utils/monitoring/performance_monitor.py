
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import psutil

logger = logging.getLogger(__name__)

class SystemPerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            'response_times_ms': [],
            'cpu_usage': [],
            'memory_usage': [],
            'timestamps': [],
            'total_errors': 0
        }
        self.thresholds = {
            'max_response_time_ms': 1000,
            'max_cpu_percent': 80,
            'max_memory_mb': 512,
            'max_network_latency_ms': 100
        }
        self.is_monitoring = False

    async def monitor_resources(self):
        while self.is_monitoring:
            self.metrics['timestamp'] = datetime.utcnow()
            self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
            self.metrics['cpu_usage'].append(psutil.cpu_percent())
            logger.info(f"System metrics: {self.metrics}")
            await asyncio.sleep(60)

    def start_monitoring(self):
        self.is_monitoring = True
        asyncio.create_task(self.monitor_resources())

    def stop_monitoring(self):
        self.is_monitoring = False

    def record_metrics(self, response_time_ms: float):
        self.metrics['response_times_ms'].append(response_time_ms)
        self.metrics['timestamps'].append(datetime.now())

    def get_metrics(self) -> Dict[str, Any]:
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': self.metrics,
            'status': 'critical' if self.metrics['total_errors'] > 10 else 'normal'
        }

    def track_time(self, operation_name: str):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = datetime.now()
                result = await func(*args, **kwargs)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds() * 1000
                self.record_metrics(execution_time)
                return result
            return wrapper
        return decorator

    def save_metrics(self):
        try:
            logger.info("Saving performance metrics: %s", self.metrics)
            return True
        except Exception as e:
            logger.error("Failed to save metrics: %s", str(e))
            return False

system_performance_monitor = SystemPerformanceMonitor()

def init_performance_monitor():
    """Initialize and return the performance monitor instance"""
    return system_performance_monitor

__all__ = ['SystemPerformanceMonitor', 'system_performance_monitor', 'init_performance_monitor']
