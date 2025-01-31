import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AuditSystem:
    def __init__(self):
        self.audit_records: List[Dict[str, Any]] = []
        
    def log_audit_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> None:
        audit_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        self.audit_records.append(audit_record)
        logger.info(f"Audit event logged: {event_type} by user {user_id}")
        
    def get_user_audit_trail(self, user_id: str) -> List[Dict[str, Any]]:
        return [
            record for record in self.audit_records
            if record['user_id'] == user_id
        ]