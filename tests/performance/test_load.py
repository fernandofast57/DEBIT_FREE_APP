
import pytest
from app import create_app
from app.utils.optimization import OptimizationService
from app.models.models import User, GoldAccount, Transaction
from time import time
import concurrent.futures
from flask import url_for

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

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
    app = create_app()
    with app.app_context():
        optimizer = OptimizationService()
        start_time = time()
        users = optimizer.optimize_query(User).limit(10).all()
        query_time = time() - start_time
        
        assert query_time < 1.0  # Query should complete within 1 second
        assert len(users) <= 10

def test_response_time(client):
    """Test API endpoint response times"""
    start_time = time()
    response = client.get('/')
    response_time = time() - start_time
    
    assert response_time < 0.5  # Response should be under 500ms
    assert response.status_code == 200

def test_transformation_performance(client):
    """Test transformation endpoint performance"""
    start_time = time()
    response = client.post('/api/v1/transformations/transform',
        json={"euro_amount": 100.00, "fixing_price": 50.00})
    transform_time = time() - start_time
    
    assert transform_time < 2.0  # Transformation should complete within 2 seconds
    assert response.status_code in [200, 201]

def test_database_bulk_operations():
    """Test bulk database operations performance"""
    app = create_app()
    with app.app_context():
        optimizer = OptimizationService()
        start_time = time()
        
        # Test bulk insert performance
        test_transactions = [Transaction(amount=100, type="TEST") for _ in range(1000)]
        optimizer.bulk_insert(test_transactions)
        
        bulk_time = time() - start_time
        assert bulk_time < 5.0  # Bulk operations should complete within 5 seconds
