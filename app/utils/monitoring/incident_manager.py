import logging
from datetime import datetime
from typing import Dict, List, Optional
from app.utils.monitoring.operator_notifications import OperatorNotificationSystem

class GestoreIncidenti:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_system = OperatorNotificationSystem()
        self.active_incidents: Dict[str, Dict] = {}
        self.incident_history: List[Dict] = []

    async def register_incident(self, incident_type: str, details: Dict, severity: str = 'medium'):
        """Registra un nuovo incidente"""
        incident_id = f"{incident_type}_{datetime.utcnow().timestamp()}"
        incident = {
            'id': incident_id,
            'type': incident_type,
            'details': details,
            'severity': severity,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'resolved_at': None
        }
        self.active_incidents[incident_id] = incident
        await self.notification_system.notify_incident(incident_type, {**details, 'severity': severity})
        self.logger.error(f"New incident registered: {incident_type} - {severity}")
        return incident_id

    async def resolve_incident(self, incident_id: str, resolution_notes: str):
        """Risolve un incidente attivo"""
        if incident_id in self.active_incidents:
            incident = self.active_incidents.pop(incident_id)
            incident['status'] = 'resolved'
            incident['resolved_at'] = datetime.utcnow()
            incident['resolution_notes'] = resolution_notes
            self.incident_history.append(incident)
            await self.notification_system.send_system_alert(
                'incident_resolved',
                f"Incident {incident_id} resolved: {resolution_notes}",
                'info'
            )
            return True
        return False