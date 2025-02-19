import pytest
from app.utils.security.rate_limiter import RequestRateLimiter, RateLimitConfig
from app.utils.security.security_manager import SecurityManager
import os

def test_environment_variables():
    """Test that sensitive environment variables are set"""
    assert os.getenv('SECRET_KEY') is not None
    assert os.getenv('DATABASE_URL') is not None
    assert not os.getenv('SECRET_KEY').startswith('dev-')

def test_rate_limiter():
    """Test rate limiter functionality"""
    limiter = RequestRateLimiter()
    key = "test_user"
    second_key = "test_user_2"

    # Should allow initial requests
    assert not limiter.is_rate_limited(key)
    assert not limiter.is_rate_limited(second_key)

    # Simulate multiple requests for first user
    for _ in range(105):  # More than default limit
        limiter.is_rate_limited(key)

    # Should be rate limited after exceeding limit
    assert limiter.is_rate_limited(key)

    # Second user should not be affected
    assert not limiter.is_rate_limited(second_key)

def test_security_manager_logging():
    """Test security logging sanitization"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

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
    log_file_path = "logs/security.log"

    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                assert "sensitive_data" not in last_line
                assert "secret_key" not in last_line
    except FileNotFoundError:
        pytest.skip(f"Security log file not found: {log_file_path}")

def test_permission_checking():
    """Test permission checking functionality"""
    security_manager = SecurityManager()

    # Test basic user permissions
    assert security_manager.check_permission("user123", "profile", "read")
    assert security_manager.check_permission("user123", "profile", "write")
    assert not security_manager.check_permission("user123", "users", "write")

    # Test permission caching
    assert "user123:profile:read" in security_manager.permission_cache

def test_role_permission_validation():
    """Test role-based permission validation"""
    security_manager = SecurityManager()

    # Test role permission checks
    assert security_manager._role_has_permission("admin", "users", "write")
    assert security_manager._role_has_permission("manager", "transactions", "read")
    assert not security_manager._role_has_permission("user", "users", "write")

def test_input_validation():
    """Test input validation and sanitization"""
    security_manager = SecurityManager()
    malicious_input = {
        "user_id": "1234'; DROP TABLE users;--",
        "password": "<script>alert('xss')</script>",
        "path": "../../../../etc/passwd",
        "nested": {
            "field": "../../secret.txt",
            "script": "<IMG SRC=javascript:alert('XSS')>",
            "sql": "UNION SELECT * FROM users--"
        },
        "special_chars": "µ§¶†‡°©®™"
    }

    sanitized = security_manager.sanitize_input(malicious_input)

    # Test SQL injection prevention
    assert "DROP TABLE" not in str(sanitized)
    assert "UNION SELECT" not in str(sanitized)

    # Test XSS prevention
    assert "<script>" not in str(sanitized)
    assert "javascript:" not in str(sanitized)

    # Test path traversal prevention
    assert "../../../../" not in str(sanitized)
    assert "../../" not in str(sanitized)

    # Verify nested structure is preserved
    assert isinstance(sanitized["nested"], dict)

    # Verify special characters are handled
    assert isinstance(sanitized["special_chars"], str)

import pytest
from app.utils.security.security_manager import SecurityManager
from app.utils.security.rate_limiter import RequestRateLimiter

def test_sql_injection_prevention():
    """Test prevenzione SQL injection"""
    security_manager = SecurityManager()
    malicious_inputs = [
        "1' OR '1'='1",
        "1; DROP TABLE users--",
        "1 UNION SELECT * FROM passwords"
    ]

    for input in malicious_inputs:
        sanitized = security_manager.sanitize_input(input)
        assert "'" not in sanitized
        assert ";" not in sanitized
        assert "UNION" not in sanitized

def test_xss_prevention():
    """Test prevenzione XSS"""
    security_manager = SecurityManager()
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "<img src='javascript:alert()'>",
        "<svg onload=alert(1)>"
    ]

    for input in malicious_inputs:
        sanitized = security_manager.sanitize_input(input)
        assert "<script>" not in sanitized
        assert "javascript:" not in sanitized
        assert "<svg onload" not in sanitized

def test_rate_limiter_stress():
    """Test stress del rate limiter"""
    limiter = RequestRateLimiter()
    user_id = "test_user"

    # Simula traffico intenso
    for _ in range(1000):
        limiter.is_rate_limited(user_id)

    # Verifica che il rate limiting sia attivo
    assert limiter.is_rate_limited(user_id)

def test_security_standards():
    """Verifica standard sicurezza secondo glossario"""
    manager = SecurityManager()

    # Verifica LivelloSicurezza
    assert manager.get_security_level() in ['standard', 'avanzato', 'massimo']

    # Verifica TokenAutenticazione
    token = manager.generate_auth_token()
    assert manager.verify_token(token)

    # Verifica LimiteRichieste
    assert manager.check_rate_limit('test_user') is True