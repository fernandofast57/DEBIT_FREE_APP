from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Callable

db_operation_duration = Histogram(
    'db_operation_duration_seconds',
    'Time spent in database operations',
    ['operation_type']
)

db_errors = Counter(
    'db_errors_total',
    'Total number of database errors',
    ['error_type']
)

concurrent_users = Gauge(
    'concurrent_users',
    'Number of concurrent users'
)

memory_usage = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes'
)

cache_hits = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

def get_performance_metrics():
    """Get current performance metrics."""
    return {
        'concurrent_users': concurrent_users._value.get(),
        'memory_usage': memory_usage._value.get(),
        'cache_hits': cache_hits._value.get(),
        'db_errors': db_errors._value.get()
    }

def monitor_db_operation(operation_type: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                db_errors.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                duration = time.time() - start_time
                db_operation_duration.labels(operation_type=operation_type).observe(duration)
        return wrapper
    return decorator

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}

    def record_metrics(self, metric_type: str, value: float):
        """Record and analyze performance metrics"""
        self.metrics.setdefault(metric_type, []).append(value)

        # Calculate moving averages
        window = min(10, len(self.metrics[metric_type]))
        moving_avg = sum(self.metrics[metric_type][-window:]) / window if window > 0 else 0

        # Alert on anomalies
        if value > moving_avg * 1.5:  # 50% above moving average
            logger.warning(f"Performance anomaly detected in {metric_type}")
            self.alert_anomaly(metric_type, value, moving_avg)

    def alert_anomaly(self, metric_type, value, moving_avg):
        #Add your anomaly alert logic here
        pass

import logging
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.daily_performance = daily_performance
        self.weekly_performance = weekly_performance
        self.monthly_performance = monthly_performance
        self.market_risk = market_risk
        self.operational_risk = operational_risk

    def record_daily_performance(self, metrics_data: Dict[str, float]) -> None:
        self.daily_performance.labels(type="daily_performance").observe(metrics_data)

    def record_weekly_performance(self, metrics_data: Dict[str, float]) -> None:
        self.weekly_performance.labels(type="weekly_performance").observe(metrics_data)

    def record_monthly_performance(self, metrics_data: Dict[str, float]) -> None:
        self.monthly_performance.labels(type="monthly_performance").observe(metrics_data)

    def update_risk_metrics(self, risk_type: str, value: float) -> None:
        if risk_type == "market_risk":
            self.market_risk.set(value)
        elif risk_type == "operational_risk":
            self.operational_risk.set(value)

    def record_cache_hit(self) -> None:
        self.cache_hits.inc()

    def get_current_metrics(self) -> Dict[str, Any]:
        return get_performance_metrics()