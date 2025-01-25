
import logging
from functools import wraps
from flask import abort, request
from app.utils.structure_validator import StructureValidator

logger = logging.getLogger(__name__)

def check_glossary_compliance():
    """Middleware che verifica la conformità con il glossario"""
    validator = StructureValidator()
    
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Verifica nomi delle variabili
            if not validator.validate_variable_names(request.get_json() if request.is_json else {}):
                logger.error("Variable names violate glossary standards")
                abort(400, "Invalid variable names")
                
            # Verifica stati delle transazioni
            if 'status' in (request.get_json() or {}):
                status = request.get_json()['status']
                if not validator.validate_transaction_status(status):
                    logger.error(f"Invalid transaction status: {status}")
                    abort(400, "Invalid transaction status")
                    
            return f(*args, **kwargs)
        return wrapper
    return decorator
