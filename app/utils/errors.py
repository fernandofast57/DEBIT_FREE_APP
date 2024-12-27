
from flask import jsonify

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str = "Validation failed"):
        self.message = message
        super().__init__(self.message)

class InvalidRankError(Exception):
    """Custom exception for invalid noble rank operations"""
    def __init__(self, message: str = "Invalid noble rank"):
        self.message = message
        super().__init__(self.message)

class InsufficientBalanceError(Exception):
    """Custom exception for insufficient balance operations"""
    def __init__(self, message: str = "Insufficient balance"):
        self.message = message
        super().__init__(self.message)

def register_error_handlers(app):
    """Register error handlers for the application."""
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500
