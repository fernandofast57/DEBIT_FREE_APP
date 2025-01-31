import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.monitoring.alert_system import AlertSystem

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self._metrics = {
            'request_count': 0,
            'error_count': 0,
            'response_times': [],
            'operation_metrics': {},
            'last_collection': datetime.utcnow().isoformat()
        }

    def collect_metric(self, name: str, value: Any) -> None:
        try:
            self._metrics[name] = value
            self._metrics['last_collection'] = datetime.utcnow().isoformat()
        except Exception as e:
            logger.error(f"Errore nella raccolta della metrica {name}: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics

    def reset(self) -> None:
        self.__init__()

    def record_operation_time(self, operation: str, duration: float) -> None:
        if operation not in self._metrics['operation_metrics']:
            self._metrics['operation_metrics'][operation] = []
        self._metrics['operation_metrics'][operation].append(duration)

metrics_collector = MetricsCollector()


class PerformanceMetrics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_system = AlertSystem()

    def track_transformation(self, user_id: int, amount: float, duration_ms: float):
        if duration_ms > 1500:  # Standard response time threshold
            self.alert_system.notify("slow_transformation", {
                "user_id": user_id,
                "duration": duration_ms
            })

        self.logger.info(f"Transformation completed: user={user_id} amount={amount} duration={duration_ms}ms")

    def track_blockchain_operation(self, operation: str, status: str, details: Dict[str, Any]):
        self.logger.info(f"Blockchain operation {operation}: status={status}")
        if status == "failed":
            self.alert_system.notify("blockchain_error", details)