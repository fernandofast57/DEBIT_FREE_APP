from datetime import datetime, timedelta
from typing import Dict, Any
import time
import logging

logger = logging.getLogger(__name__)

class AsyncMonitor:
    def __init__(self):
        self.ongoing_operations = {}
        self.metrics = {
            'response_times': [],
            'failed_operations': 0,
            'completed_operations': 0,
            'concurrent_operations': 0,
            'operation_types': {
                'blockchain': {'success': 0, 'failure': 0},
                'database': {'success': 0, 'failure': 0},
                'api': {'success': 0, 'failure': 0}
            }
        }
        self.thresholds = {
            'max_response_time': 5.0,
            'max_concurrent_ops': 100,
            'max_queue_length': 50,
            'max_failure_rate': 0.05
        }

    async def register_operation(self, operation_id: str, operation_type: str) -> None:
        self.ongoing_operations[operation_id] = {
            'type': operation_type,
            'start_time': time.time(),
            'status': 'running'
        }
        self.metrics['concurrent_operations'] = len(self.ongoing_operations)

    async def complete_operation(self, operation_id: str, success: bool = True) -> None:
        if operation_id in self.ongoing_operations:
            duration = time.time() - self.ongoing_operations[operation_id]['start_time']
            operation_type = self.ongoing_operations[operation_id]['type']

            if success:
                self.metrics['completed_operations'] += 1
                self.metrics['operation_types'][operation_type]['success'] += 1
            else:
                self.metrics['failed_operations'] += 1
                self.metrics['operation_types'][operation_type]['failure'] += 1

            self.metrics['response_times'].append(duration)
            del self.ongoing_operations[operation_id]

    def get_metrics_report(self) -> Dict[str, Any]:
        return {
            'metrics': self.metrics,
            'thresholds': self.thresholds,
            'timestamp': datetime.utcnow().isoformat()
        }

    def clear_old_metrics(self, days: int = 7) -> None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.metrics['response_times'] = [
            t for t in self.metrics['response_times'] 
            if datetime.utcfromtimestamp(t) > cutoff
        ]