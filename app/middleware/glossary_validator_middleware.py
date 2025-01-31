
from functools import wraps
from flask import abort, request
from app.utils.structure_validator import StructureValidator
import logging

logger = logging.getLogger(__name__)
validator = StructureValidator()

def validate_glossary_terms():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                
                # Validate states and types
                if 'operation_type' in data and data['operation_type'] not in ['gold_purchase', 'gold_sale', 'gold_transfer']:
                    logger.error(f"Invalid operation type: {data['operation_type']}")
                    abort(400, "Operation type not compliant with glossary")
                    
                if 'operation_status' in data and data['operation_status'] not in ['started', 'processing', 'completed', 'failed']:
                    logger.error(f"Invalid operation status: {data['operation_status']}")
                    abort(400, "Operation status not compliant with glossary")
                    
                if 'noble_rank' in data and data['noble_rank'] not in ['bronze', 'silver', 'gold']:
                    logger.error(f"Invalid noble rank: {data['noble_rank']}")
                    abort(400, "Noble rank not compliant with glossary")
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator
