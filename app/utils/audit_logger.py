
import logging
from datetime import datetime
from functools import wraps
from flask import g, request
from typing import Callable

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_action(self, action_type: str, user_id: int, details: str):
        self.logger.info(
            f"ACTION: {action_type} | USER: {user_id} | DETAILS: {details}")

audit_logger = AuditLogger()

def require_operator_approval(f: Callable):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user.is_operator:
            raise PermissionError("Richiesta autorizzazione operatore")
            
        result = f(*args, **kwargs)
        
        audit_logger.log_action(
            action_type=f.__name__,
            user_id=g.user.id,
            details=f"Operazione eseguita: {request.url}"
        )
        return result
    return decorated

def require_admin_approval(f: Callable):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user.is_admin:
            raise PermissionError("Richiesta autorizzazione amministratore")
            
        result = f(*args, **kwargs)
        
        audit_logger.log_action(
            action_type=f.__name__,
            user_id=g.user.id, 
            details=f"Approvazione amministratore: {request.url}"
        )
        return result
    return decorated
