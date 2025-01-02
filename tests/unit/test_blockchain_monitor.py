
import pytest
from unittest.mock import Mock, patch
from app.utils.blockchain_monitor import BlockchainMonitor
from decimal import Decimal
from web3.exceptions import BlockNotFound, TransactionNotFound

@pytest.fixture
def blockchain_monitor():
    return BlockchainMonitor()

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
async def test_network_interruption():
    """Test behavior during network interruption"""
    monitor = BlockchainMonitor()
    with patch('web3.Web3.eth.get_block') as mock_block:
        mock_block.side_effect = BlockNotFound
        response = await monitor.process_block(12345)
        assert response['status'] == 'error'
        assert 'block not found' in response['message'].lower()

@pytest.mark.asyncio
async def test_invalid_transaction():
    """Test handling of invalid transaction"""
    monitor = BlockchainMonitor()
    with patch('web3.Web3.eth.get_transaction') as mock_tx:
        mock_tx.side_effect = TransactionNotFound
        response = await monitor.verify_transaction('0x1234')
        assert response['status'] == 'error'
        assert 'transaction not found' in response['message'].lower()

def test_gas_price_threshold():
    """Test gas price monitoring"""
    monitor = BlockchainMonitor()
    with patch('web3.Web3.eth.gas_price') as mock_gas:
        mock_gas.return_value = 100000000000  # 100 Gwei
        assert monitor.is_gas_price_acceptable() is False

def test_concurrent_transactions():
    """Test handling multiple transactions simultaneously"""
    monitor = BlockchainMonitor()
    transactions = ['0x1234', '0x5678', '0x9abc']
    with patch('web3.Web3.eth.get_transaction_count') as mock_count:
        mock_count.return_value = len(transactions)
        assert monitor.can_process_transactions(transactions) is True

@pytest.mark.asyncio
async def test_empty_block():
    """Test handling of empty blocks"""
    monitor = BlockchainMonitor()
    with patch('web3.Web3.eth.get_block') as mock_block:
        mock_block.return_value = {'transactions': []}
        response = await monitor.process_block(12345)
        assert response['status'] == 'success'
        assert len(response.get('transactions', [])) == 0

@pytest.mark.asyncio
async def test_malformed_transaction():
    """Test handling of malformed transaction data"""
    monitor = BlockchainMonitor()
    with patch('web3.Web3.eth.get_transaction') as mock_tx:
        mock_tx.return_value = {'hash': '0x1234', 'value': None}
        response = await monitor.verify_transaction('0x1234')
        assert response['status'] == 'error'
        assert 'invalid transaction data' in response['message'].lower()

def test_extreme_gas_prices():
    """Test handling of extreme gas prices"""
    monitor = BlockchainMonitor()
    test_cases = [
        (0, True),  # Zero gas price
        (1000000000000000, False),  # Extremely high gas price
        (1, True)  # Minimum gas price
    ]
    with patch('web3.Web3.eth.gas_price') as mock_gas:
        for price, expected in test_cases:
            mock_gas.return_value = price
            assert monitor.is_gas_price_acceptable() == expected

@pytest.mark.asyncio
async def test_network_timeout():
    """Test handling of network timeouts"""
    monitor = BlockchainMonitor()
    with patch('web3.Web3.eth.get_block') as mock_block:
        mock_block.side_effect = TimeoutError("Request timed out")
        response = await monitor.process_block(12345)
        assert response['status'] == 'error'
        assert 'timeout' in response['message'].lower()
