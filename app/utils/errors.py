
class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str = "Validation failed"):
        self.message = message
        super().__init__(self.message)
