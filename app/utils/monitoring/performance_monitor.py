# app/utils/monitoring/performance_monitor.py
import time
import json
from datetime import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PerformanceMonitor:

    def __init__(self):
        self.metrics = []
        self.start_time = time.time()

    def record_metrics(self, metrics: Dict[str, Any]):
        """Registra metriche con timestamp"""
        metrics['timestamp'] = datetime.utcnow().isoformat()
        self.metrics.append(metrics)

        # Log delle metriche se superano soglie critiche
        if metrics.get('memory_mb', 0) > 1000:  # 1GB
            logger.warning(f"High memory usage: {metrics['memory_mb']}MB")
        if metrics.get('cpu_percent', 0) > 80:
            logger.warning(f"High CPU usage: {metrics['cpu_percent']}%")

    def save_metrics(self):
        """Salva le metriche su file"""
        try:
            with open('logs/performance_metrics.json', 'a') as f:
                for metric in self.metrics:
                    json.dump(metric, f)
                    f.write('\n')
            self.metrics = []  # Reset dopo il salvataggio
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
