
import pytest
from web3 import Web3
from app import create_app
from app.utils.blockchain_monitor import BlockchainMonitor

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app

@pytest.fixture
def w3():
    return Web3(Web3.HTTPProvider(get_test_rpc_url()))

@pytest.fixture
def blockchain_monitor(w3):
    return BlockchainMonitor(w3)

@pytest.fixture
def auth_headers():
    return {
        'Authorization': 'Bearer valid-test-token',
        'X-User-Id': '123'
    }

def get_test_rpc_url():
    return "http://localhost:8545"  # Test RPC URL
