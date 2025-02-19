import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque  # <-- IMPORTA deque
from app.utils.monitoring.alert_system import SistemaAllarmi

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

    # ### INIZIO DEL METODO AGGIUNTO: ###
    async def collect_system_metrics(self):
        """Raccoglie metriche di sistema (CPU, memoria, ecc.)"""
        import psutil  # Importa psutil *dentro* il metodo (lazy import)
        self.collect_metric('cpu_usage_percent', psutil.cpu_percent())
        self.collect_metric('memory_usage_percent',
                            psutil.virtual_memory().percent)
        # ... (potresti aggiungere altre metriche di sistema qui, es. disk_usage, network_latency, ecc. se vuoi) ...
        logger.info("Metriche di sistema raccolte")

    # ### FINE DEL METODO AGGIUNTO ###


metrics_collector = MetricsCollector()


class PerformanceMetrics:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_system = SistemaAllarmi()

    def track_transformation(self, user_id: int, amount: float,
                             duration_ms: float):
        if duration_ms > 1500:  # Standard response time threshold
            self.alert_system.notify("slow_transformation", {
                "user_id": user_id,
                "duration": duration_ms
            })

        self.logger.info(
            f"Transformation completed: user={user_id} amount={amount} duration={duration_ms}ms"
        )

    def track_blockchain_operation(self, operation: str, status: str,
                                   details: Dict[str, Any]):
        self.logger.info(f"Blockchain operation {operation}: status={status}")
        if status == "failed":
            self.alert_system.notify("blockchain_error", details)
