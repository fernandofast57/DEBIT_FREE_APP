
from typing import Dict, Any
import logging
from app.models.models import User, GoldTransformation
from app.utils.performance_monitor import performance_monitor

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
