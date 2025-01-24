
from functools import wraps
from flask import abort
from app.utils.structure_validator import StructureValidator
import logging

logger = logging.getLogger(__name__)
validator = StructureValidator()

def enforce_glossary_compliance():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            validation_results = validator.validate_structure()
            
            # Verifica tutti i risultati della validazione
            all_valid = all(
                all(result if isinstance(result, bool) else all(result.values())
                    for result in section.values())
                for section in validation_results.values()
            )
            
            if not all_valid:
                logger.error("Glossary compliance check failed")
                # Log dettagliato dei fallimenti
                for section, results in validation_results.items():
                    for check, result in results.items():
                        if not result:
                            logger.error(f"Validation failed: {section}.{check}")
                abort(500, description="Application naming violates glossary standards")
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
