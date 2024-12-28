
import pytest
from app import create_app
from app.utils.optimization import OptimizationService
from app.models.models import User, GoldAccount
from time import time
import concurrent.futures
from flask import url_for

def test_concurrent_requests(client):
    """Test handling of multiple concurrent requests"""
    def make_request():
        return client.get('/')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        responses = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in responses)

def test_query_optimization():
    """Test database query optimization"""
    optimizer = OptimizationService()
    start_time = time()
    users = optimizer.optimize_query(User).limit(10).all()
    query_time = time() - start_time
    
    assert query_time < 1.0  # Query should complete within 1 second
    assert len(users) <= 10  # Verify limit is applied
    assert isinstance(users, list)  # Verify we get a list back

def test_response_time(client):
    """Test API endpoint response times"""
    start_time = time()
    response = client.get('/')
    response_time = time() - start_time
    
    assert response_time < 0.5  # Response should be under 500ms
    assert response.status_code == 200
import pytest
from app import create_app
from config import Config
import time

@pytest.fixture
def app():
    app = create_app(Config())
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_api_response_time(client):
    """Test API endpoint response times"""
    start_time = time.time()
    response = client.get('/')
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.2  # Response should be under 200ms

def test_database_query_performance(client):
    """Test database query performance"""
    start_time = time()
    response = client.get('/api/v1/transformations')
    end_time = time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.3  # Query should complete under 300ms
