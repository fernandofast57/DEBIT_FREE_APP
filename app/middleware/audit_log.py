
from functools import wraps
from flask import g, request
from app.utils.audit_logger import audit_logger

def audit_log(event_type):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                audit_logger.log_action(
                    action_type=event_type,
                    user_id=getattr(g, 'user', {}).get('id', 0),
                    details=f"{event_type} on {request.path}"
                )
                return result
            except Exception as e:
                audit_logger.log_action(
                    action_type=f"{event_type}_error",
                    user_id=getattr(g, 'user', {}).get('id', 0),
                    details=f"Error in {event_type}: {str(e)}"
                )
                raise
        return wrapper
    return decorator
