import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from statistics import mean, median

logger = logging.getLogger(__name__)

class AggregatoreMetriche:
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'response_times': [],
            'transaction_costs': [],
            'error_rates': [],
            'system_loads': []
        }
        self.aggregation_intervals = {
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(days=7)
        }
        self.timestamps: List[datetime] = []

    def add_metric(self, metric_type: str, value: float) -> None:
        if metric_type not in self.metrics:
            self.metrics[metric_type] = []
        self.metrics[metric_type].append(value)
        self.timestamps.append(datetime.utcnow())
        logger.debug(f"Added {metric_type} metric: {value}")

    def get_aggregated_stats(self, metric_type: str, interval: str = 'hourly') -> Dict[str, float]:
        if metric_type not in self.metrics:
            return {}

        cutoff_time = datetime.utcnow() - self.aggregation_intervals[interval]
        recent_metrics = [
            value for value, timestamp in zip(self.metrics[metric_type], self.timestamps)
            if timestamp > cutoff_time
        ]

        if not recent_metrics:
            return {}

        return {
            'average': mean(recent_metrics),
            'median': median(recent_metrics),
            'min': min(recent_metrics),
            'max': max(recent_metrics),
            'count': len(recent_metrics)
        }

    def clear_old_metrics(self, days: int = 30) -> None:
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        for metric_type in self.metrics:
            self.metrics[metric_type] = [
                value for value, timestamp in zip(self.metrics[metric_type], self.timestamps)
                if timestamp > cutoff_time
            ]
        self.timestamps = [ts for ts in self.timestamps if ts > cutoff_time]
        logger.info(f"Cleared metrics older than {days} days")