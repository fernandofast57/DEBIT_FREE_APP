
from typing import Dict, Any

class GoldInvestmentError(Exception):
    """Base exception class as defined in glossary"""
    pass

class TransformationError(GoldInvestmentError):
    """Error during gold transformation process"""
    pass

class NobleSystemError(GoldInvestmentError):
    """Error in noble system operations"""
    pass

class SecurityError(GoldInvestmentError):
    """Security related errors"""
    pass
from typing import Dict, Any

class GoldInvestmentError(Exception):
    """Base exception class for the application"""
    pass

class TransformationError(GoldInvestmentError):
    """Error during gold transformation process"""
    pass

class NobleSystemError(GoldInvestmentError):
    """Error in noble system operations"""
    pass
