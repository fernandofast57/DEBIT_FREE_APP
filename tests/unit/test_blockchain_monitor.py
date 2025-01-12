
import pytest
from unittest.mock import Mock, patch
from app.utils.blockchain_monitor import BlockchainMonitor
from decimal import Decimal
from web3.exceptions import BlockNotFound, TransactionNotFound

@pytest.fixture
def web3_mock():
    mock = Mock()
    mock.eth = Mock()
    mock.eth.gas_price = 50000000000  # 50 Gwei
    mock.eth.get_block = Mock()
    mock.eth.get_transaction = Mock()
    mock.eth.get_transaction_count = Mock()
    return mock

@pytest.fixture
def blockchain_monitor(web3_mock):
    return BlockchainMonitor(web3_mock)

@pytest.mark.asyncio
async def test_basic_monitoring(blockchain_monitor):
    """Test basic blockchain monitoring functionality"""
    with patch.object(blockchain_monitor.w3.eth, 'get_block') as mock_get_block:
        mock_block = {'number': 1000, 'transactions': []}
        mock_get_block.return_value = mock_block
        await blockchain_monitor.monitor_transactions()
        assert blockchain_monitor.latest_block == mock_block

def test_transaction_validation(blockchain_monitor):
    """Test transaction validation with various amounts"""
    test_cases = [
        (Decimal('0.001'), True),
        (Decimal('1000000.0'), True),
        (Decimal('0.0'), False),
        (Decimal('-1.0'), False),
    ]
    
    for amount, expected in test_cases:
        assert blockchain_monitor.validate_transaction_amount(amount) == expected

@pytest.mark.asyncio
async def test_network_interruption(web3_mock):
    """Test behavior during network interruption"""
    monitor = BlockchainMonitor(web3_mock)
    web3_mock.eth.get_block.side_effect = BlockNotFound
    response = await monitor.process_block(12345)
    assert response['status'] == 'error'
    assert 'block not found' in response['message'].lower()

@pytest.mark.asyncio
async def test_invalid_transaction(web3_mock):
    """Test handling of invalid transaction"""
    monitor = BlockchainMonitor(web3_mock)
    web3_mock.eth.get_transaction.side_effect = TransactionNotFound
    response = await monitor.verify_transaction('0x1234')
    assert response['status'] == 'error'
    assert 'transaction not found' in response['message'].lower()

def test_concurrent_transactions(blockchain_monitor):
    """Test handling multiple transactions simultaneously"""
    transactions = ['0x1234', '0x5678', '0x9abc']
    blockchain_monitor.w3.eth.get_transaction_count.return_value = len(transactions)
    assert blockchain_monitor.can_process_transactions(transactions) is True

@pytest.mark.asyncio
async def test_empty_block(web3_mock):
    """Test handling of empty blocks"""
    monitor = BlockchainMonitor(web3_mock)
    web3_mock.eth.get_block.return_value = {'transactions': []}
    response = await monitor.process_block(12345)
    assert response['status'] == 'success'
    assert len(response.get('transactions', [])) == 0

@pytest.mark.asyncio
async def test_malformed_transaction(web3_mock):
    """Test handling of malformed transaction data"""
    monitor = BlockchainMonitor(web3_mock)
    web3_mock.eth.get_transaction.return_value = {'hash': '0x1234', 'value': None}
    response = await monitor.verify_transaction('0x1234')
    assert response['status'] == 'error'
    assert 'invalid transaction data' in response['message'].lower()

def test_extreme_gas_prices(blockchain_monitor):
    """Test handling of extreme gas prices"""
    test_cases = [
        (0, True),
        (1_000_000_000_000_000, False),
        (10, True)
    ]
    for price, expected in test_cases:
        with patch.object(blockchain_monitor.w3.eth, 'gas_price', return_value=price):
            assert blockchain_monitor.is_gas_price_acceptable() == expected

@pytest.mark.asyncio
async def test_network_timeout(web3_mock):
    """Test handling of network timeouts"""
    monitor = BlockchainMonitor(web3_mock)
    web3_mock.eth.get_block.side_effect = TimeoutError("Request timed out")
    response = await monitor.process_block(12345)
    assert response['status'] == 'error'
    assert 'timeout' in response['message'].lower()
import pytest
from unittest.mock import Mock, patch
from app.utils.blockchain_monitor import BlockchainMonitor
from web3 import Web3

@pytest.fixture
def mock_w3():
    w3 = Mock(spec=Web3)
    w3.eth.get_block_number.return_value = 1000
    return w3

@pytest.fixture
def blockchain_monitor(mock_w3):
    return BlockchainMonitor(mock_w3)

def test_monitor_transaction(blockchain_monitor):
    tx_data = {
        'type': 'gold_transformation',
        'status': 'success',
        'tx_hash': '0x123'
    }
    result = blockchain_monitor.monitor_transactions(tx_data)
    assert result['status'] == 'monitored'

def test_alert_system(blockchain_monitor):
    result = blockchain_monitor.send_alert("Test alert")
    assert result['status'] == 'sent'

def test_block_monitoring(blockchain_monitor, mock_w3):
    mock_w3.eth.get_block_number.return_value = 1001
    assert blockchain_monitor.check_new_blocks()
