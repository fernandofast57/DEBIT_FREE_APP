
from functools import wraps
from flask import request, jsonify
from app.utils.structure_validator import StructureValidator

validator = StructureValidator()

def validate_structure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        results = validator.validate_structure()
        if not all(results.values()):
            return jsonify({
                'error': 'Invalid project structure',
                'details': results
            }), 500
        return f(*args, **kwargs)
    return decorated_function
