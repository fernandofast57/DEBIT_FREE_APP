import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceMonitor:
    def __init__(self):
        self.service_status = {}
        self.service_metrics = {
            'response_times': {},
            'availability': {},
            'errors': {}
        }
        self.performance_thresholds = {
            'max_response_time': 2000,  # ms
            'min_availability': 0.99,   # 99%
            'error_threshold': 5        # errors per minute
        }

    async def register_operation_metric(self, service_name: str, operation: str, duration: float) -> None:
        if service_name not in self.service_metrics['response_times']:
            self.service_metrics['response_times'][service_name] = {}

        if operation not in self.service_metrics['response_times'][service_name]:
            self.service_metrics['response_times'][service_name][operation] = []

        self.service_metrics['response_times'][service_name][operation].append(duration)
        if duration * 1000 > self.performance_thresholds['max_response_time']:
            logger.warning(f"Operation {operation} in {service_name} exceeded threshold: {duration * 1000}ms")

    def update_service_status(self, service_name: str, available: bool) -> None:
        self.service_status[service_name] = {
            'available': available,
            'last_check': datetime.utcnow().isoformat()
        }

    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        return {
            'status': self.service_status.get(service_name, {'available': False}),
            'response_times': self.service_metrics['response_times'].get(service_name, {}),
            'timestamp': datetime.utcnow().isoformat()
        }

class SecurityMonitor:
    def __init__(self):
        self.security_events = []
        self.access_attempts = {}
        self.violations = []
        self.alert_thresholds = {
            'max_failed_attempts': 5,
            'violation_threshold': 3,
            'monitoring_interval': 300  # 5 minutes
        }

    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        self.security_events.append({
            'type': event_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })

    def register_access_attempt(self, user_id: str, success: bool) -> None:
        if user_id not in self.access_attempts:
            self.access_attempts[user_id] = {'failed': 0, 'last_attempt': None}

        if not success:
            self.access_attempts[user_id]['failed'] += 1

        self.access_attempts[user_id]['last_attempt'] = datetime.utcnow()

    def get_security_metrics(self) -> Dict[str, Any]:
        return {
            'total_events': len(self.security_events),
            'recent_violations': len(self.violations),
            'high_risk_users': [uid for uid, data in self.access_attempts.items() 
                              if data['failed'] >= self.alert_thresholds['max_failed_attempts']],
            'timestamp': datetime.utcnow().isoformat()
        }