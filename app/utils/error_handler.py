
from functools import wraps
import logging
import traceback
from typing import Callable, Any, Optional, Dict
from flask import jsonify, current_app
from datetime import datetime

logger = logging.getLogger(__name__)

class BusinessError(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class SecurityError(BusinessError):
    def __init__(self, message: str, error_code: str = 'SECURITY_ERROR'):
        super().__init__(message, error_code, status_code=403)

class ValidationError(BusinessError):
    def __init__(self, message: str, error_code: str = 'VALIDATION_ERROR'):
        super().__init__(message, error_code, status_code=400)

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        except BusinessError as e:
            error_details = {
                'error': e.error_code,
                'message': e.message,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.error(f"Business error: {error_details}")
            return jsonify(error_details), e.status_code
        except Exception as e:
            error_id = str(int(time.time()))
            error_details = {
                'error': 'INTERNAL_ERROR',
                'error_id': error_id,
                'message': 'Un errore interno è occorso'
            }
            logger.critical(
                f"Critical error {error_id}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            return jsonify(error_details), 500
    return wrapper

def log_error(error: Exception, context: Optional[Dict] = None):
    """Utility per logging centralizzato degli errori"""
    error_details = {
        'error_type': error.__class__.__name__,
        'message': str(error),
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    if isinstance(error, BusinessError):
        logger.error(f"Business error: {error_details}")
    else:
        logger.critical(f"System error: {error_details}\n{traceback.format_exc()}")
