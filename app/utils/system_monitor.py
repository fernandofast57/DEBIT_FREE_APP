
import psutil
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': []
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
            
            # Store metrics history
            self.metrics['cpu_usage'].append(metrics['cpu_percent'])
            self.metrics['memory_usage'].append(metrics['memory_percent'])
            self.metrics['disk_usage'].append(metrics['disk_percent'])
            
            # Alert on high resource usage
            if metrics['cpu_percent'] > 80:
                logger.warning(f"High CPU usage detected: {metrics['cpu_percent']}%")
            if metrics['memory_percent'] > 85:
                logger.warning(f"High memory usage detected: {metrics['memory_percent']}%")
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

system_monitor = SystemMonitor()
