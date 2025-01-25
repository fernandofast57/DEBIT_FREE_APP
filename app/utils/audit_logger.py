
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
from decimal import Decimal
import logging
import json
from datetime import datetime

class TransformationAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('transformation_audit')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('logs/transformations_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - Transaction ID: %(transaction_id)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_transformation(self, transaction_id: str, user_id: int, 
                         euro_amount: Decimal, gold_grams: Decimal, 
                         fixing_price: Decimal) -> None:
        """Log detailed transformation data"""
        log_data = {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'euro_amount': str(euro_amount),
            'gold_grams': str(gold_grams),
            'fixing_price': str(fixing_price),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(
            "Transformation executed",
            extra={'transaction_id': transaction_id},
            exc_info=True
        )
        
        # Log dettagliato in formato JSON
        with open('logs/detailed_transformations.json', 'a') as f:
            json.dump(log_data, f)
            f.write('\n')
from decimal import Decimal
import logging
import json
from datetime import datetime

class DetailedAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('detailed_audit')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('logs/detailed_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - ID: %(transaction_id)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_transformation(self, transaction_id: str, user_id: int, 
                         euro_amount: Decimal, gold_grams: Decimal, 
                         fixing_price: Decimal, noble_rank: str) -> None:
        """Log dettagliato delle trasformazioni con tracking noble"""
        log_data = {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'euro_amount': str(euro_amount),
            'gold_grams': str(gold_grams),
            'fixing_price': str(fixing_price),
            'noble_rank': noble_rank,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(
            f"Transformation: {json.dumps(log_data)}",
            extra={'transaction_id': transaction_id}
        )
