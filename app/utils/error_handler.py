
from functools import wraps
import logging
import traceback
from flask import jsonify
from typing import Callable, Any

logger = logging.getLogger(__name__)

class ApplicationError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except ApplicationError as e:
            logger.error(f"Application error: {str(e)}")
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            logger.critical(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper
