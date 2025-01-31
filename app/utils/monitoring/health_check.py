import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(self):
        self.services = {}
        self.thresholds = {
            'memory_usage': 85,  # percentage
            'cpu_usage': 80,     # percentage
            'response_time': 2000 # milliseconds
        }

    def check_service(self, service_name: str) -> Dict[str, Any]:
        try:
            is_healthy = service_name in self.services
            return {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'service': service_name,
                'timestamp': self.services.get(service_name, {}).get('last_check')
            }
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return {'status': 'error', 'service': service_name}