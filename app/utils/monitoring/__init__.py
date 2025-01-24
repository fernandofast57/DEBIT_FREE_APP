from datetime import datetime
import psutil
import logging

from .monitoring_setup import setup_monitoring
from .performance import monitor_performance
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


def monitor_performance():
  """
    Monitor system performance metrics
    """
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


__all__ = ['setup_monitoring', 'monitor_performance', 'PerformanceMonitor']
# Monitoring package initialization