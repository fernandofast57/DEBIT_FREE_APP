import psutil
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    value: float
    timestamp: datetime
    status: str

class SaluteSistema:
    def __init__(self):
        self.metrics_history: Dict[str, deque] = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'disk': deque(maxlen=100),
            'network': deque(maxlen=100)
        }
        self.thresholds = {
            'cpu_critical': 90,
            'cpu_warning': 80,
            'memory_critical': 90,
            'memory_warning': 85,
            'disk_critical': 95,
            'disk_warning': 90
        }
        self.last_check = datetime.now()

    def collect_health_metrics(self) -> Dict[str, Any]:
        try:
            current_time = datetime.now()
            metrics = {
                'timestamp': current_time.isoformat(),
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_stats': self._get_network_stats(),
                'system_uptime': self._get_uptime(),
                'process_count': len(psutil.pids())
            }

            self._update_metrics_history(metrics)
            self._log_critical_metrics(metrics)

            return metrics
        except Exception as e:
            logger.error(f"Error collecting system health metrics: {str(e)}")
            return {}

    def _get_network_stats(self) -> Dict[str, float]:
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }

    def _get_uptime(self) -> float:
        return time.time() - psutil.boot_time()

    def _update_metrics_history(self, metrics: Dict[str, Any]) -> None:
        timestamp = datetime.now()
        self.metrics_history['cpu'].append(HealthMetric(
            metrics['cpu_usage'], timestamp, self._get_status('cpu', metrics['cpu_usage'])
        ))
        self.metrics_history['memory'].append(HealthMetric(
            metrics['memory_usage'], timestamp, self._get_status('memory', metrics['memory_usage'])
        ))
        self.metrics_history['disk'].append(HealthMetric(
            metrics['disk_usage'], timestamp, self._get_status('disk', metrics['disk_usage'])
        ))

    def _get_status(self, metric_type: str, value: float) -> str:
        if value >= self.thresholds[f'{metric_type}_critical']:
            return 'critical'
        elif value >= self.thresholds[f'{metric_type}_warning']:
            return 'warning'
        return 'healthy'

    def _log_critical_metrics(self, metrics: Dict[str, Any]) -> None:
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)) and metric_name.endswith('_usage'):
                base_name = metric_name.replace('_usage', '')
                if value >= self.thresholds.get(f'{base_name}_critical', 100):
                    logger.critical(f"{metric_name} is critical: {value}%")
                elif value >= self.thresholds.get(f'{base_name}_warning', 100):
                    logger.warning(f"{metric_name} is high: {value}%")

    def get_system_status(self) -> Dict[str, Any]:
        metrics = self.collect_health_metrics()
        status_checks = {
            'cpu_healthy': metrics.get('cpu_usage', 100) < self.thresholds['cpu_warning'],
            'memory_healthy': metrics.get('memory_usage', 100) < self.thresholds['memory_warning'],
            'disk_healthy': metrics.get('disk_usage', 100) < self.thresholds['disk_warning']
        }

        overall_status = 'healthy'
        if not all(status_checks.values()):
            if any(metrics.get(m, 0) >= self.thresholds[f"{m.split('_')[0]}_critical"] 
                  for m in ['cpu_usage', 'memory_usage', 'disk_usage']):
                overall_status = 'critical'
            else:
                overall_status = 'warning'

        return {
            'status': overall_status,
            'metrics': metrics,
            'checks': status_checks,
            'timestamp': datetime.now().isoformat()
        }

    def get_historical_metrics(self, metric_type: str, hours: int = 1) -> List[Dict[str, Any]]:
        if metric_type not in self.metrics_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            {
                'value': m.value,
                'timestamp': m.timestamp.isoformat(),
                'status': m.status
            }
            for m in self.metrics_history[metric_type]
            if m.timestamp > cutoff_time
        ]