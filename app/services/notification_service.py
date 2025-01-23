
from typing import Dict, Any
import logging
from app.models.models import User, GoldTransformation
from app.utils.monitoring.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)

class NotificationService:
    @performance_monitor.track_time('notification')
    async def notify_transformation(self, user: User, transformation: GoldTransformation) -> Dict[str, Any]:
        try:
            message = {
                'user_id': user.id,
                'type': 'transformation',
                'data': {
                    'euro_amount': float(transformation.euro_amount),
                    'gold_grams': float(transformation.gold_grams),
                    'status': transformation.status,
                    'timestamp': transformation.created_at.isoformat()
                }
            }
            
            logger.info(f"Notification sent for transformation {transformation.id}")
            return {'status': 'success', 'message': message}
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return {'status': 'error', 'message': str(e)}
            
    @performance_monitor.track_time('notification')
    async def get_user_notifications(self, user_id: int) -> list:
        """Recupera le notifiche dell'utente."""
        try:
            notifications = []
            transformations = await GoldTransformation.query.filter_by(user_id=user_id).order_by(GoldTransformation.created_at.desc()).limit(10).all()
            
            for transformation in transformations:
                notifications.append({
                    'type': 'transformation',
                    'data': {
                        'euro_amount': float(transformation.euro_amount),
                        'gold_grams': float(transformation.gold_grams),
                        'status': transformation.status,
                        'timestamp': transformation.created_at.isoformat()
                    }
                })
            
            return notifications
        except Exception as e:
            logger.error(f"Error fetching notifications: {str(e)}")
            return []
from typing import List
from datetime import datetime
from app.models import User, Notification
from app.database import db

class NotificationService:
    @staticmethod
    async def send_notification(user_id: int, message: str, type: str = "info"):
        notification = Notification(
            user_id=user_id,
            message=message,
            type=type,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        await db.session.commit()

    @staticmethod
    async def get_user_notifications(user_id: int, limit: int = 10) -> List[dict]:
        notifications = await db.session.query(Notification)\
            .filter(Notification.user_id == user_id)\
            .order_by(Notification.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [n.to_dict() for n in notifications]
