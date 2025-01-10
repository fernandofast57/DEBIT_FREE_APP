
import pytest
from unittest.mock import Mock, patch
from app.utils.blockchain_monitor import BlockchainMonitor
from decimal import Decimal
from web3.exceptions import BlockNotFound, TransactionNotFound

@pytest.fixture
def web3_mock():
    mock = Mock()
    mock.eth.gas_price = 50000000000  # 50 Gwei
    return mock

@pytest.fixture
def blockchain_monitor(web3_mock):
    return BlockchainMonitor(web3_mock)

def test_basic_monitoring(blockchain_monitor):
    """Test basic blockchain monitoring functionality"""
    with patch('web3.Web3.eth.get_block_number') as mock_block:
        mock_block.return_value = 1000
        assert blockchain_monitor.get_latest_block() == 1000

def test_transaction_validation(blockchain_monitor):
    """Test transaction validation with various amounts"""
    test_cases = [
        (Decimal('0.001'), True),  # Minimum amount
        (Decimal('1000000.0'), True),  # Large amount
        (Decimal('0.0'), False),  # Zero amount
        (Decimal('-1.0'), False),  # Negative amount
    ]
    
    for amount, expected in test_cases:
        assert blockchain_monitor.validate_transaction_amount(amount) == expected

@pytest.mark.asyncio
async def test_network_interruption(web3_mock):
    """Test behavior during network interruption"""
    monitor = BlockchainMonitor(web3_mock)
    with patch('web3.Web3.eth.get_block') as mock_block:
        mock_block.side_effect = BlockNotFound
        response = await monitor.process_block(12345)
        assert response['status'] == 'error'
        assert 'block not found' in response['message'].lower()

@pytest.mark.asyncio
async def test_invalid_transaction(web3_mock):
    """Test handling of invalid transaction"""
    monitor = BlockchainMonitor(web3_mock)
    with patch('web3.Web3.eth.get_transaction') as mock_tx:
        mock_tx.side_effect = TransactionNotFound
        response = await monitor.verify_transaction('0x1234')
        assert response['status'] == 'error'
        assert 'transaction not found' in response['message'].lower()

def test_gas_price_threshold(blockchain_monitor):
    """Test gas price monitoring"""
    with patch.object(blockchain_monitor.w3.eth, 'gas_price', return_value=100000000000):  # 100 Gwei
        assert blockchain_monitor.is_gas_price_acceptable() is False

def test_concurrent_transactions(blockchain_monitor):
    """Test handling multiple transactions simultaneously"""
    transactions = ['0x1234', '0x5678', '0x9abc']
    with patch('web3.Web3.eth.get_transaction_count') as mock_count:
        mock_count.return_value = len(transactions)
        assert blockchain_monitor.can_process_transactions(transactions) is True

@pytest.mark.asyncio
async def test_empty_block(web3_mock):
    """Test handling of empty blocks"""
    monitor = BlockchainMonitor(web3_mock)
    with patch('web3.Web3.eth.get_block') as mock_block:
        mock_block.return_value = {'transactions': []}
        response = await monitor.process_block(12345)
        assert response['status'] == 'success'
        assert len(response.get('transactions', [])) == 0

@pytest.mark.asyncio
async def test_malformed_transaction(web3_mock):
    """Test handling of malformed transaction data"""
    monitor = BlockchainMonitor(web3_mock)
    with patch('web3.Web3.eth.get_transaction') as mock_tx:
        mock_tx.return_value = {'hash': '0x1234', 'value': None}
        response = await monitor.verify_transaction('0x1234')
        assert response['status'] == 'error'
        assert 'invalid transaction data' in response['message'].lower()

def test_extreme_gas_prices(blockchain_monitor):
    """Test handling of extreme gas prices"""
    test_cases = [
        (0, True),  # Zero gas price
        (1000000000000000, False),  # Extremely high gas price
        (1, True)  # Minimum gas price
    ]
    for price, expected in test_cases:
        with patch.object(blockchain_monitor.w3.eth, 'gas_price', return_value=price):
            assert blockchain_monitor.is_gas_price_acceptable() == expected

@pytest.mark.asyncio
async def test_network_timeout(web3_mock):
    """Test handling of network timeouts"""
    monitor = BlockchainMonitor(web3_mock)
    with patch('web3.Web3.eth.get_block') as mock_block:
        mock_block.side_effect = TimeoutError("Request timed out")
        response = await monitor.process_block(12345)
        assert response['status'] == 'error'
        assert 'timeout' in response['message'].lower()
