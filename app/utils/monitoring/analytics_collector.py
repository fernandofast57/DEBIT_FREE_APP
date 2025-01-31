import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CollettoreAnalisi:
    def __init__(self):
        self.analytics_data: Dict[str, Any] = {
            'transactions': [],
            'transformations': [],
            'user_activities': [],
            'system_metrics': []
        }

    def collect_metric(self, category: str, data: Dict[str, Any]) -> None:
        if category not in self.analytics_data:
            logger.warning(f"Invalid category: {category}")
            return

        data['timestamp'] = datetime.utcnow().isoformat()
        self.analytics_data[category].append(data)

    def get_analytics(self, category: str, time_range: int = 24) -> List[Dict[str, Any]]:
        """Get analytics for the last n hours"""
        if category not in self.analytics_data:
            return []

        cutoff = datetime.utcnow() - timedelta(hours=time_range)
        return [
            entry for entry in self.analytics_data[category]
            if datetime.fromisoformat(entry['timestamp']) > cutoff
        ]