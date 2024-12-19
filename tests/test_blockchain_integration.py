
import pytest
from unittest.mock import Mock, patch
from app.services.blockchain_service import BlockchainService
from web3 import Web3

@pytest.fixture
def blockchain_service():
    service = BlockchainService()
    service.w3 = Mock()
    return service

def test_contract_deployment(blockchain_service):
    blockchain_service.w3.eth.contract.return_value = Mock()
    result = blockchain_service.deploy_contract()
    assert result is not None

@patch('web3.Web3.HTTPProvider')
def test_connection(mock_provider):
    service = BlockchainService()
    assert service.w3 is not None
    assert service.w3.isConnected()
