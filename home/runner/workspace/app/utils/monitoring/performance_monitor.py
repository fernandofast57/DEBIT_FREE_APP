
import logging
import asyncio
from datetime import datetime
import psutil
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SystemPerformanceMonitor:
    _instance: Optional['SystemPerformanceMonitor'] = None
    
    def __init__(self):
        self.metrics = {
            'response_times_ms': [],
            'cpu_usage': [],
            'memory_usage': [],
            'blockchain_metrics': {
                'transaction_count': 0,
                'gas_used': [],
                'block_times': []
            },
            'timestamps': [],
            'total_errors': 0
        }
        self.is_monitoring = False

    @classmethod
    def get_instance(cls) -> 'SystemPerformanceMonitor':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_monitoring(self):
        """Start the monitoring system"""
        self.is_monitoring = True
        asyncio.create_task(self._monitor_resources())

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False

    async def _monitor_resources(self):
        """Monitor system resources"""
        while self.is_monitoring:
            self.metrics['cpu_usage'].append(psutil.cpu_percent())
            self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
            self.metrics['timestamps'].append(datetime.utcnow())
            await asyncio.sleep(60)

    def save_metrics(self) -> bool:
        """Save current metrics to storage"""
        try:
            logger.info("Saving performance metrics: %s", self.metrics)
            return True
        except Exception as e:
            logger.error("Failed to save metrics: %s", str(e))
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': self.metrics,
            'status': 'critical' if self.metrics['total_errors'] > 10 else 'normal'
        }

def init_performance_monitor() -> SystemPerformanceMonitor:
    """Initialize and return the performance monitor instance"""
    return SystemPerformanceMonitor.get_instance()

__all__ = ['SystemPerformanceMonitor', 'init_performance_monitor']
