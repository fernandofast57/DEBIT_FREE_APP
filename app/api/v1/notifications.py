
from flask import Blueprint, jsonify
from app.utils.auth import auth_required
from app.services.notification_service import NotificationService

bp = Blueprint('notifications', __name__)
notification_service = NotificationService()

@bp.route('/api/v1/notifications', methods=['GET'])
@auth_required
async def get_notifications():
    try:
        user_id = g.user.id
        notifications = await notification_service.get_user_notifications(user_id)
        return jsonify(notifications)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
