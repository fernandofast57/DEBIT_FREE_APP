import logging
from functools import wraps
from typing import Callable, Any, Dict
from flask import jsonify
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

class SystemError(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except SystemError as e:
            logger.error(f"System error: {str(e)}")
            return jsonify({
                'error': e.error_code,
                'message': e.message,
                'timestamp': datetime.utcnow().isoformat()
            }), e.status_code
        except BusinessError as e:
            error_details = {
                'error': e.error_code,
                'message': e.message,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.error(f"Business error: {error_details}")
            return jsonify(error_details), e.status_code
        except Exception as e:
            logger.critical(f"Critical error: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'INTERNAL_ERROR',
                'message': 'Si è verificato un errore interno',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    return wrapper

def log_error(error: Exception, context: Dict = None):
    error_details = {
        'error_type': error.__class__.__name__,
        'message': str(error),
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    logger.error(f"Error details: {error_details}")