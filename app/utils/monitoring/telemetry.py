import logging
from typing import Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SistemaTelemetria:
    def __init__(self):
        self.telemetry_data: List[Dict[str, Any]] = []

    def record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        telemetry_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data
        }
        self.telemetry_data.append(telemetry_record)
        logger.info(f"Telemetry event recorded: {json.dumps(telemetry_record)}")

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        return [
            record for record in self.telemetry_data
            if record['event_type'] == event_type
        ]