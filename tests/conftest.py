import pytest
import asyncio
from unittest.mock import Mock
from web3 import Web3, EthereumTesterProvider

@pytest.fixture
def mock_web3():
    mock = Mock()
    mock.to_checksum_address = Web3.to_checksum_address
    mock.to_wei = Web3.to_wei
    return mock

@pytest.fixture
def mock_contract():
    return Mock()

@pytest.fixture
def mock_secrets(monkeypatch):
    """Mock environment secrets for testing"""
    monkeypatch.setenv('PRIVATE_KEY', '0x1234567890123456789012345678901234567890123456789012345678901234')
    monkeypatch.setenv('CONTRACT_ADDRESS', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    monkeypatch.setenv('RPC_ENDPOINTS', 'http://localhost:8545')
    return monkeypatch

@pytest.fixture
def blockchain_service(mock_web3, mock_contract, mock_secrets):
    from app.services.blockchain_service import BlockchainService
    service = BlockchainService()
    service.web3 = mock_web3
    service.contract = mock_contract
    return service

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

import pytest
from config import TestConfig

@pytest.fixture
def test_config():
    """Fixture for test configuration"""
    return TestConfig()

@pytest.fixture
def app(test_config):
    """Fixture for Flask app with test configuration"""
    from app import create_app
    app = create_app(test_config)
    return app