import logging
from datetime import datetime
from typing import Dict, Any
from app.utils.monitoring.alert_system import AlertSystem
from app.services.notification_service import NotificationService

class NotificheOperatore: #Renamed class as requested
    def __init__(self):
        self.alert_system = AlertSystem()
        self.notification_service = NotificationService()
        self.logger = logging.getLogger(__name__)

    async def notify_incident(self, incident_type: str, details: Dict[str, Any]):
        """Notifica gli operatori di un incidente"""
        message = {
            'type': 'incident',
            'timestamp': datetime.utcnow().isoformat(),
            'incident_type': incident_type,
            'details': details,
            'severity': details.get('severity', 'medium')
        }
        await self.notification_service.send_notification(
            user_id=0,  # Sistema
            message=str(message),
            type='operator_alert'
        )
        self.logger.warning(f"Incident notification sent: {incident_type}")

    async def send_system_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Invia alert di sistema agli operatori"""
        await self.notification_service.send_notification(
            user_id=0,
            message=f"[{alert_type.upper()}] {message}",
            type=f"system_{severity}"
        )