import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CollettoreMetriche:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'error_count': 0,
            'response_times': [],
            'last_collection': time.time()
        }

    def collect_metric(self, metric_name: str, value: Any) -> None:
        try:
            self.metrics[metric_name] = value
            self.metrics['last_collection'] = time.time()
        except Exception as e:
            logger.error(f"Error collecting metric {metric_name}: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics