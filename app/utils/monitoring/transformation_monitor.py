import logging
from typing import Dict, Any
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TransformationMonitor:
    def __init__(self):
        self.transformations = {}
        self.metrics = {
            'successful_transformations': 0,
            'failed_transformations': 0,
            'total_amount_transformed': 0.0
        }

    def record_transformation(self, user_id: int, amount: float, success: bool) -> None:
        timestamp = datetime.utcnow().isoformat()
        if user_id not in self.transformations:
            self.transformations[user_id] = []

        self.transformations[user_id].append({
            'timestamp': timestamp,
            'amount': amount,
            'success': success
        })

        if success:
            self.metrics['successful_transformations'] += 1
            self.metrics['total_amount_transformed'] += amount
        else:
            self.metrics['failed_transformations'] += 1
            logger.warning(f"Failed transformation for user {user_id}: {amount}")

    def get_metrics(self) -> Dict[str, Any]:
        return {
            'metrics': self.metrics,
            'last_updated': datetime.utcnow().isoformat()
        }

class TransformationMonitorV2: #Added V2 to distinguish from the newly added class
    def __init__(self):
        self.logger = logging.getLogger('transformation.monitor')
        self.metrics = {
            'daily_metrics': {},
            'weekly_metrics': {},
            'monthly_metrics': {},
            'total_count': 0,
            'success_count': 0,
            'error_count': 0,
            'processing_times': [],
            'amounts': [],
            'statuses': {},
            'errors': {}
        }
        self.alert_thresholds = {
            'max_processing_time': 30,  # seconds
            'max_error_rate': 0.1,      # 10%
            'min_success_rate': 0.95    # 95%
        }
        self._status_types = frozenset(['initiated', 'processing', 'completed', 'failed'])
        self._max_metrics_length = 1000

    async def record_metric(self, metric_data: Dict[str, Any]) -> None:
        if metric_data['status'] not in self._status_types:
            raise ValueError(f"Invalid status. Must be one of {self._status_types}")

        await self._update_metrics(metric_data)
        self.logger.info(f"Transformation metric recorded: {metric_data}")

    async def _update_metrics(self, metric_data: Dict[str, Any]) -> None:
        timestamp = datetime.fromisoformat(metric_data['timestamp'])
        day_key = timestamp.strftime('%Y-%m-%d')

        # Control metrics length to prevent memory issues
        if len(self.metrics['processing_times']) > self._max_metrics_length:
            self.metrics['processing_times'] = self.metrics['processing_times'][-self._max_metrics_length:]
        if len(self.metrics['amounts']) > self._max_metrics_length:
            self.metrics['amounts'] = self.metrics['amounts'][-self._max_metrics_length:]

        if day_key not in self.metrics['daily_metrics']:
            self.metrics['daily_metrics'][day_key] = {
                'total_count': 0,
                'total_euro_amount': Decimal('0'),
                'total_gold_grams': Decimal('0'),
                'status_counts': {status: 0 for status in self._status_types}
            }

        self.metrics['daily_metrics'][day_key]['total_count'] += 1
        self.metrics['daily_metrics'][day_key]['total_euro_amount'] += Decimal(metric_data['euro_amount'])
        self.metrics['daily_metrics'][day_key]['total_gold_grams'] += Decimal(metric_data['gold_grams'])
        self.metrics['daily_metrics'][day_key]['status_counts'][metric_data['status']] += 1
        self.metrics['total_count'] +=1
        if metric_data['status'] == 'completed':
            self.metrics['success_count'] += 1
        elif metric_data['status'] == 'failed':
            self.metrics['error_count'] +=1
        self.metrics['processing_times'].append(metric_data.get('processing_time',0)) #added processing time
        self.metrics['amounts'].append(metric_data['euro_amount'])


    async def check_alert_thresholds(self) -> Dict[str, Any]:
        alerts = []

        if self.metrics['processing_times']:
            avg_time = sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])
            if avg_time > self.alert_thresholds['max_processing_time']:
                alerts.append(f"Average processing time ({avg_time}s) exceeds threshold")

        if self.metrics['total_count'] > 0:
            error_rate = self.metrics['error_count'] / self.metrics['total_count']
            if error_rate > self.alert_thresholds['max_error_rate']:
                alerts.append(f"Error rate ({error_rate:.2%}) exceeds threshold")

            success_rate = self.metrics['success_count'] / self.metrics['total_count']
            if success_rate < self.alert_thresholds['min_success_rate']:
                alerts.append(f"Success rate ({success_rate:.2%}) below threshold")

        return {
            'has_alerts': bool(alerts),
            'alerts': alerts,
            'timestamp': datetime.utcnow().isoformat()
        }