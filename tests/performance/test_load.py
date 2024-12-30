
import pytest
import asyncio
from time import time
from app import create_app
from app.config.constants import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig())
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_api_response_time(client):
    """Test API endpoint response times"""
    start_time = time()
    response = client.get('/api/v1/health')
    response_time = time() - start_time
    
    assert response_time < 0.5  # Response should be under 500ms
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_blockchain_monitor_performance(app):
    """Test blockchain monitoring performance"""
    with app.app_context():
        from app.utils.blockchain_monitor import BlockchainMonitor
        from web3 import Web3
        
        w3 = Web3()
        monitor = BlockchainMonitor(w3)
        
        start_time = time()
        metrics = await monitor.monitor_network()
        execution_time = time() - start_time
        
        assert execution_time < 2.0  # Should complete within 2 seconds
        assert 'latest_block' in metrics
