
from typing import Dict, Any, List
import logging
from datetime import datetime
from app.models.models import User, Notification
from app.database import db

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def send_notification(self, user_id: int, message: str, type: str = "info") -> Dict[str, Any]:
        try:
            notification = Notification(
                user_id=user_id,
                message=message,
                type=type,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            await db.session.commit()
            
            return {
                'status': 'success',
                'notification_id': notification.id
            }
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    async def get_user_notifications(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            notifications = await db.session.query(Notification)\
                .filter(Notification.user_id == user_id)\
                .order_by(Notification.created_at.desc())\
                .limit(limit)\
                .all()
                
            return [
                {
                    'id': n.id,
                    'message': n.message,
                    'type': n.type,
                    'created_at': n.created_at.isoformat()
                }
                for n in notifications
            ]
            
        except Exception as e:
            self.logger.error(f"Error fetching notifications: {str(e)}")
            return []

    async def mark_as_read(self, notification_id: int) -> Dict[str, Any]:
        try:
            notification = await db.session.query(Notification).get(notification_id)
            if notification:
                notification.read = True
                await db.session.commit()
                return {'status': 'success'}
            return {'status': 'error', 'message': 'Notification not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
