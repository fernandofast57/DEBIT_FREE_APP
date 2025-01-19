from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()

    def record_metric(self, category: str, value: float):
        if category not in self.metrics:
            self.metrics[category] = []
        self.metrics[category].append(value)
        logger.debug(f"Recorded metric {category}: {value}")

    def get_metrics(self, category: Optional[str] = None) -> Dict:
        if category:
            return {category: self.metrics.get(category, [])}
        return self.metrics

    def clear_metrics(self, category: Optional[str] = None):
        if category:
            self.metrics[category] = []
        else:
            self.metrics.clear()

performance_monitor = PerformanceMonitor()