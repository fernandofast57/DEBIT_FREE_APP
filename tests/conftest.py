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
def blockchain_service(mock_web3, mock_contract):
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
from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Use EthereumTesterProvider for testing
    WEB3_PROVIDER = Web3(EthereumTesterProvider())
    CHAIN_ID = 1337  # Local test chain ID