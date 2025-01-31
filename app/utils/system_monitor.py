import psutil
import logging
from datetime import datetime
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.system_metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': [],
            'response_times': [],
            'error_counts': {},
            'endpoint_usage': {},
            'active_users': set()
        }

    def collect_system_metrics(self) -> Dict[str, Any]:
        try:
            system_metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_bytes_sent': psutil.net_io_counters().bytes_sent,
                'network_bytes_recv': psutil.net_io_counters().bytes_recv
            }

            self.system_metrics['cpu_usage'].append(system_metrics['cpu_percent'])
            self.system_metrics['memory_usage'].append(system_metrics['memory_percent'])
            self.system_metrics['disk_usage'].append(system_metrics['disk_percent'])

            if system_metrics['cpu_percent'] > 80:
                logger.warning(f"High CPU usage detected: {system_metrics['cpu_percent']}%")
            if system_metrics['memory_percent'] > 85:
                logger.warning(f"High memory usage detected: {system_metrics['memory_percent']}%")

            return system_metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

    def log_request(self, endpoint: str) -> None:
        if endpoint not in self.system_metrics['endpoint_usage']:
            self.system_metrics['endpoint_usage'][endpoint] = 0
        self.system_metrics['endpoint_usage'][endpoint] += 1

    def log_error(self, error_type: str) -> None:
        if error_type not in self.system_metrics['error_counts']:
            self.system_metrics['error_counts'][error_type] = 0
        self.system_metrics['error_counts'][error_type] += 1

    def log_response_time(self, time: float) -> None:
        self.system_metrics['response_times'].append(time)

    def get_average_response_time(self) -> float:
        if not self.system_metrics['response_times']:
            return 0.0
        return sum(self.system_metrics['response_times']) / len(self.system_metrics['response_times'])