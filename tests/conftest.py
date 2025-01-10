import pytest
from app import create_app
from app.database import db
from web3 import Web3
from app.utils.blockchain_monitor import BlockchainMonitor

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def w3():
    provider = Web3.HTTPProvider('https://polygon-mumbai.infura.io/v3/YOUR-PROJECT-ID')
    w3 = Web3(provider)
    if not w3.is_connected():
        pytest.skip("Blockchain connection not available")
    return w3

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