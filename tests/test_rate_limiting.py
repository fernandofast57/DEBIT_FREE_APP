
import pytest
import time
import redis
from unittest.mock import Mock, patch
from flask import Flask
from app.utils.security.rate_limiter import RobustRateLimiter, rate_limit

@pytest.fixture
def app():
    """Fixture per l'app Flask"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def redis_client():
    """Fixture per il client Redis"""
    return redis.Redis(host='0.0.0.0', port=6379, db=0)

@pytest.fixture
def rate_limiter(redis_client):
    """Fixture per il rate limiter"""
    return RobustRateLimiter(redis_url='redis://0.0.0.0:6379/0')

@pytest.fixture
def mock_request():
    """Fixture per mock delle richieste"""
    request = Mock()
    request.remote_addr = '127.0.0.1'
    request.user = Mock()
    request.user.id = 1
    return request

class TestRobustRateLimiter:
    """Test suite per il sistema di rate limiting"""

    def test_local_rate_limiting(self, rate_limiter, mock_request):
        """Test del rate limiting locale"""
        with patch('flask.request', mock_request):
            limit = RateLimit(requests=2, window=1)
            key = "test_local"
            
            allowed, remaining = rate_limiter._check_local(key, limit)
            assert allowed is True
            assert remaining == 1
            
            allowed, remaining = rate_limiter._check_local(key, limit)
            assert allowed is True
            assert remaining == 0
            
            allowed, remaining = rate_limiter._check_local(key, limit)
            assert allowed is False
            assert remaining < 0

    @pytest.mark.redis
    def test_redis_rate_limiting(self, rate_limiter, mock_request, redis_client):
        """Test del rate limiting con Redis"""
        with patch('flask.request', mock_request):
            limit = RateLimit(requests=2, window=1)
            key = "test_redis"
            
            redis_client.delete(key)
            
            allowed, remaining = rate_limiter._check_redis(key, limit)
            assert allowed is True
            assert remaining == 1
            
            allowed, remaining = rate_limiter._check_redis(key, limit)
            assert allowed is True
            assert remaining == 0
            
            allowed, remaining = rate_limiter._check_redis(key, limit)
            assert allowed is False
            assert remaining < 0

    def test_window_expiration(self, rate_limiter, mock_request):
        """Test della scadenza della finestra temporale"""
        with patch('flask.request', mock_request):
            limit = RateLimit(requests=1, window=1)
            key = "test_expiration"
            
            allowed, _ = rate_limiter._check_local(key, limit)
            assert allowed is True
            
            allowed, _ = rate_limiter._check_local(key, limit)
            assert allowed is False
            
            time.sleep(1.1)
            
            allowed, _ = rate_limiter._check_local(key, limit)
            assert allowed is True

    @pytest.mark.redis
    def test_redis_window_expiration(self, rate_limiter, mock_request, redis_client):
        """Test della scadenza della finestra temporale con Redis"""
        with patch('flask.request', mock_request):
            limit = RateLimit(requests=1, window=1)
            key = "test_redis_expiration"
            
            redis_client.delete(key)
            
            allowed, _ = rate_limiter._check_redis(key, limit)
            assert allowed is True
            
            allowed, _ = rate_limiter._check_redis(key, limit)
            assert allowed is False
            
            time.sleep(1.1)
            
            allowed, _ = rate_limiter._check_redis(key, limit)
            assert allowed is True

    def test_identifier_generation(self, rate_limiter, mock_request):
        """Test della generazione degli identificatori"""
        with patch('flask.request', mock_request):
            identifier = rate_limiter._get_identifier(by_ip=True, by_user=True)
            assert '127.0.0.1' in identifier
            assert '1' in identifier
            
            identifier = rate_limiter._get_identifier(by_ip=True, by_user=False)
            assert identifier == '127.0.0.1'
            
            identifier = rate_limiter._get_identifier(by_ip=False, by_user=True)
            assert identifier == '1'

    @pytest.mark.parametrize('max_requests,window_size,should_pass', [
        (1, 1, True),
        (1, 1, False),
        (5, 1, True),
        (0, 1, False),
    ])
    def test_rate_limit_configurations(self, rate_limiter, mock_request, max_requests, window_size, should_pass):
        """Test di varie configurazioni di rate limiting"""
        with patch('flask.request', mock_request):
            limit = RateLimit(max_requests=max_requests, window_size=window_size)
            key = f"test_config_{max_requests}_{window_size}"
            allowed, _ = rate_limiter._check_local(key, limit)
            assert allowed is should_pass

    @pytest.mark.redis
    def test_redis_failure_fallback(self, app, mock_request):
        """Test del fallback in caso di errore Redis"""
        with patch('flask.request', mock_request):
            limiter = RobustRateLimiter(redis_url='redis://nonexistent:6379/0')
            limit = RateLimit(requests=1, window=1)
            allowed, _ = limiter.is_allowed("test_fallback", limit)
            assert allowed is True
