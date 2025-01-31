import logging
from typing import Dict, Any, List
from datetime import datetime
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

class SistemaAllarmi:
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.severity_levels = {
            'info': 0,
            'warning': 1,
            'critical': 2,
            'emergency': 3
        }
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'error_rate': 5.0,
            'response_time': 2000,
            'network_latency': 500,
            'database_connections': 100,
            'request_queue': 1000
        }
        self.alert_counts = {level: 0 for level in self.severity_levels}
        self.last_alert_time = datetime.utcnow()
        self.metrics_history: Dict[str, deque] = {
            metric: deque(maxlen=100) for metric in self.alert_thresholds
        }

    def add_alert(self, message: str, severity: str = 'info', metric: str = None, value: float = None) -> None:
        try:
            if severity not in self.severity_levels:
                raise ValueError(f"Invalid severity level: {severity}")

            current_time = datetime.utcnow()
            alert = {
                'id': str(hash(f"{current_time}{message}{severity}")),
                'timestamp': current_time.isoformat(),
                'message': message,
                'severity': severity,
                'metric': metric,
                'value': value,
                'acknowledged': False
            }

            self.alerts.append(alert)
            self.alert_counts[severity] += 1
            self.last_alert_time = current_time

            if metric and value is not None:
                self.metrics_history[metric].append((current_time, value))

            log_level = logging.CRITICAL if severity in ['critical', 'emergency'] else logging.WARNING
            logger.log(log_level, f"Alert [{severity.upper()}]: {message}")

            if severity in ['critical', 'emergency']:
                self._trigger_emergency_protocols(alert)

        except Exception as e:
            logger.error(f"Error adding alert: {str(e)}")
            raise

    def _trigger_emergency_protocols(self, alert: Dict[str, Any]) -> None:
        try:
            logger.critical(f"Emergency protocols triggered for alert: {alert['id']}")
            # Add emergency handling logic here if needed
        except Exception as e:
            logger.error(f"Error in emergency protocols: {str(e)}")

    def check_threshold(self, metric: str, value: float) -> None:
        if metric in self.alert_thresholds:
            threshold = self.alert_thresholds[metric]
            if value > threshold:
                self.add_alert(
                    f"{metric} exceeded threshold: {value} > {threshold}",
                    'warning' if value < threshold * 1.2 else 'critical',
                    metric,
                    value
                )

    def get_active_alerts(self, min_severity: str = 'info') -> List[Dict[str, Any]]:
        min_level = self.severity_levels[min_severity]
        return [
            alert for alert in self.alerts
            if self.severity_levels[alert['severity']] >= min_level
        ]

    def clear_alerts(self) -> None:
        self.alerts = []

from collections import deque