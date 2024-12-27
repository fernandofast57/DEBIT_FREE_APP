
import pytest
from app.utils.security.rate_limiter import RobustRateLimiter
from app.utils.security.security_manager import SecurityManager
import os

def test_environment_variables():
    """Test that sensitive environment variables are set"""
    assert os.getenv('SECRET_KEY') is not None
    assert os.getenv('DATABASE_URL') is not None
    assert not os.getenv('SECRET_KEY').startswith('dev-')

def test_rate_limiter():
    """Test rate limiter functionality"""
    limiter = RobustRateLimiter()
    key = "test_user"
    
    # Should allow initial requests
    assert not limiter.is_rate_limited(key)
    
    # Simulate multiple requests
    for _ in range(105):  # More than default limit
        limiter.is_rate_limited(key)
    
    # Should be rate limited after exceeding limit
    assert limiter.is_rate_limited(key)

def test_security_manager_logging():
    """Test security logging sanitization"""
    security_manager = SecurityManager()
    test_event = {
        "user_id": "12345",
        "action": "login",
        "password": "sensitive_data",
        "api_key": "secret_key"
    }
    
    # Log should not contain sensitive data
    security_manager.log_security_event("test", test_event)
    
    # Read the last line of the security log
    with open("logs/gold-investment_security.log", "r") as f:
        last_line = f.readlines()[-1]
        assert "sensitive_data" not in last_line
        assert "secret_key" not in last_line
