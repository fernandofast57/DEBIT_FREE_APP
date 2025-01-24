
import time
import asyncio
import functools
import logging
import psutil
from typing import Dict, Any, Optional
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, alert_threshold: float = 0.1):
        self.alert_threshold = alert_threshold
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.cache_hits: Dict[str, int] = {}
        self.start_time = datetime.now()
        self._shutdown_flag = False
        self.logger = logging.getLogger(__name__)

    def _init_operation_metrics(self, operation: str) -> None:
        if operation not in self.metrics:
            self.metrics[operation] = {
                'count': 0,
                'total_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf'),
                'average_time': 0.0,
                'memory_usage': 0,
                'cache_hits': 0,
                'last_execution': None,
                'alerts': [],
                'performance_score': 100.0
            }
            self.cache_hits[operation] = 0

    def record_cache_hit(self, operation: str) -> None:
        if operation not in self.cache_hits:
            self.cache_hits[operation] = 0
        self.cache_hits[operation] += 1
        if operation in self.metrics:
            self.metrics[operation]['cache_hits'] = self.cache_hits[operation]

    def track_memory_usage(self, operation: str) -> None:
        process = psutil.Process()
        memory_info = process.memory_info()
        self.metrics[operation]['memory_usage'] = memory_info.rss

    def track_time(self, category: str):
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._init_operation_metrics(category)
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    self._update_metrics(category, execution_time)
                    self.track_memory_usage(category)
                    
                    if execution_time > self.alert_threshold:
                        self.metrics[category]['alerts'].append({
                            'timestamp': datetime.now(),
                            'execution_time': execution_time,
                            'threshold': self.alert_threshold
                        })
                    
                    return result
                except Exception as e:
                    self.logger.error(f"Error in {category}: {str(e)}")
                    raise

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._init_operation_metrics(category)
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    self._update_metrics(category, execution_time)
                    self.track_memory_usage(category)
                    
                    if execution_time > self.alert_threshold:
                        self.metrics[category]['alerts'].append({
                            'timestamp': datetime.now(),
                            'execution_time': execution_time,
                            'threshold': self.alert_threshold
                        })
                    
                    return result
                except Exception as e:
                    self.logger.error(f"Error in {category}: {str(e)}")
                    raise

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator

    def _update_metrics(self, category: str, execution_time: float) -> None:
        metrics = self.metrics[category]
        metrics['count'] += 1
        metrics['total_time'] += execution_time
        metrics['max'] = max(metrics.get('max_time', 0), execution_time)
        metrics['min'] = min(metrics.get('min_time', float('inf')), execution_time)
        metrics['average'] = metrics['total_time'] / metrics['count']
        metrics['last_execution'] = datetime.now()

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        return self.metrics

    def save_metrics(self) -> None:
        if not self._shutdown_flag:
            self._shutdown_flag = True
            self.logger.info(f"Saving metrics before shutdown: {self.metrics}")

performance_monitor = PerformanceMonitor()
