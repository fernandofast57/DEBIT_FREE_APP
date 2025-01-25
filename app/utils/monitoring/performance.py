import time
import asyncio
import functools
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, field
import psutil

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    total_time: float = 0.0
    count: int = 0
    max_time: float = 0.0
    min_time: float = float('inf')
    recent_times: List[float] = field(default_factory=list)
    
    def add_measurement(self, execution_time: float):
        self.total_time += execution_time
        self.count += 1
        self.max_time = max(self.max_time, execution_time)
        self.min_time = min(self.min_time, execution_time)
        self.recent_times.append(execution_time)
        if len(self.recent_times) > 10:
            self.recent_times.pop(0)
    
    @property
    def average_time(self) -> float:
        return self.total_time / self.count if self.count > 0 else 0.0
    
    @property
    def recent_average(self) -> float:
        return sum(self.recent_times) / len(self.recent_times) if self.recent_times else 0.0

class EnhancedPerformanceMonitor:
    def __init__(self, alert_threshold: float = 1.0):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.alert_threshold = alert_threshold
        self.start_time = datetime.now()
    
    def track_time(self, category: str):
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metric(category, execution_time)
                    return result
                except Exception as e:
                    logger.error(f"Error in {category}: {str(e)}")
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metric(category, execution_time)
                    return result
                except Exception as e:
                    logger.error(f"Error in {category}: {str(e)}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _record_metric(self, category: str, execution_time: float):
        if category not in self.metrics:
            self.metrics[category] = PerformanceMetric()
        
        self.metrics[category].add_measurement(execution_time)
        
        if execution_time > self.alert_threshold:
            logger.warning(f"Performance alert: {category} took {execution_time:.2f}s")
    
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        return {
            category: {
                'average': metric.average_time,
                'recent_average': metric.recent_average,
                'max': metric.max_time,
                'min': metric.min_time,
                'count': metric.count
            }
            for category, metric in self.metrics.items()
        }

performance_monitor_func = EnhancedPerformanceMonitor()


import psutil
import time
from datetime import datetime
import logging
from dataclasses import dataclass
from typing import Dict, List
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    active_connections: int
    response_times: List[float]

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage': 90.0
        }

    async def collect_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        metrics = SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            active_connections=len(psutil.net_connections()),
            response_times=[]
        )

        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        await self._check_alerts(metrics)
        return metrics

    async def _check_alerts(self, metrics: SystemMetrics):
        """Check if any metrics exceed thresholds"""
        for metric_name, threshold in self.alert_thresholds.items():
            value = getattr(metrics, metric_name)
            if value > threshold:
                logger.warning(f"Performance alert: {metric_name} at {value}% exceeds threshold of {threshold}%")

    async def start_monitoring(self):
        """Start continuous monitoring"""
        while True:
            await self.collect_metrics()
            await asyncio.sleep(60)  # Collect metrics every minute

performance_monitor_sys = PerformanceMonitor()

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def monitor_performance():
    """Function to monitor system performance metrics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'memory_available': memory.available,
            'memory_used': memory.used
        }

        logger.info(f"Performance metrics: {metrics}")
        return metrics

    except Exception as e:
        logger.error(f"Error monitoring performance: {e}")
        return None