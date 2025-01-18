import pytest
from unittest.mock import Mock, patch
from app.utils.monitoring.blockchain_monitor import BlockchainMonitor
from app.utils.logging_config import get_logger
from web3.exceptions import BlockNotFound
import asyncio

logger = get_logger(__name__)

@pytest.fixture
def mock_w3():
    w3 = Mock()
    w3.eth.get_block_number.return_value = 12345
    w3.eth.get_block.return_value = {
        'number': 12345,
        'timestamp': 1234567890,
        'transactions': ['0x123', '0x456']
    }
    return w3

@pytest.fixture
def monitor(mock_w3):
    return BlockchainMonitor(mock_w3)

@pytest.mark.asyncio
async def test_monitor_initialization(monitor):
    """Test corretta inizializzazione del monitor"""
    assert monitor.w3 is not None
    assert monitor.last_processed_block == 0
    assert isinstance(monitor.alert_threshold, int)

@pytest.mark.asyncio
async def test_process_new_blocks(monitor, mock_w3):
    """Test elaborazione di nuovi blocchi"""
    monitor.last_processed_block = 12344

    processed_blocks = await monitor.process_new_blocks()
    assert processed_blocks == 1
    assert monitor.last_processed_block == 12345

@pytest.mark.asyncio
async def test_handle_block_not_found(monitor, mock_w3):
    """Test gestione errore blocco non trovato"""
    mock_w3.eth.get_block.side_effect = BlockNotFound

    monitor.last_processed_block = 12344
    processed_blocks = await monitor.process_new_blocks()
    assert processed_blocks == 0

@pytest.mark.asyncio
async def test_check_network_health(monitor, mock_w3):
    """Test controllo salute della rete"""
    mock_w3.eth.syncing = False
    mock_w3.net.peer_count = 10

    health_status = await monitor.check_network_health()
    assert health_status['status'] == 'healthy'
    assert health_status['peer_count'] == 10
    assert not health_status['is_syncing']

@pytest.mark.asyncio
async def test_alert_generation(monitor, mock_w3):
    """Test generazione alert per anomalie"""
    mock_w3.eth.syncing = True
    mock_w3.net.peer_count = 1

    alerts = await monitor.generate_alerts()
    assert len(alerts) > 0
    assert any('peer count' in alert.lower() for alert in alerts)

@pytest.mark.asyncio
async def test_performance_metrics(monitor, mock_w3):
    """Test metriche di performance"""
    metrics = await monitor.get_performance_metrics()
    assert 'block_processing_time' in metrics
    assert 'blocks_per_second' in metrics
    assert isinstance(metrics['block_processing_time'], (int, float))

@pytest.mark.asyncio
async def test_monitor_recovery(monitor, mock_w3):
    """Test recupero dopo interruzione"""
    monitor.last_processed_block = 12340
    mock_w3.eth.get_block_number.return_value = 12345

    await monitor.recover_missed_blocks()
    assert monitor.last_processed_block == 12345

@pytest.mark.asyncio
async def test_concurrent_processing(monitor, mock_w3):
    """Test elaborazione concorrente dei blocchi"""
    monitor.last_processed_block = 12340
    mock_w3.eth.get_block_number.return_value = 12345

    tasks = [monitor.process_new_blocks() for _ in range(3)]
    results = await asyncio.gather(*tasks)
    assert all(r >= 0 for r in results)

@pytest.fixture
def mock_w3_original():
    w3 = Mock(spec=Web3)
    w3.eth = Mock()
    w3.eth.get_block_number.return_value = 1000
    return w3

@pytest.fixture
def blockchain_monitor_original(mock_w3_original):
    return BlockchainMonitor(mock_w3_original)


@pytest.mark.asyncio
async def test_basic_monitoring(blockchain_monitor_original):
    """Test basic blockchain monitoring functionality"""
    result = await blockchain_monitor_original.monitor_transactions()
    assert result is not None
    assert blockchain_monitor_original.latest_block is not None

def test_transaction_validation(blockchain_monitor_original):
    """Test transaction validation with various amounts"""
    test_cases = [
        (Decimal('0.001'), True),
        (Decimal('1000000.0'), True),
        (Decimal('0.0'), False),
        (Decimal('-1.0'), False),
    ]

    for amount, expected in test_cases:
        assert blockchain_monitor_original.validate_transaction_amount(amount) == expected

@pytest.mark.asyncio
async def test_network_interruption(mock_w3_original):
    """Test behavior during network interruption"""
    monitor = BlockchainMonitor(mock_w3_original)
    mock_w3_original.eth.get_block.side_effect = BlockNotFound
    response = await monitor.process_block(12345)
    assert response['status'] == 'error'
    assert 'block not found' in response['message'].lower()

@pytest.mark.asyncio
async def test_invalid_transaction(mock_w3_original):
    """Test handling of invalid transaction"""
    monitor = BlockchainMonitor(mock_w3_original)
    mock_w3_original.eth.get_transaction.side_effect = TransactionNotFound
    response = await monitor.verify_transaction('0x1234')
    assert response['status'] == 'error'
    assert 'transaction not found' in response['message'].lower()

def test_concurrent_transactions(blockchain_monitor_original):
    """Test handling multiple transactions simultaneously"""
    transactions = ['0x1234', '0x5678', '0x9abc']
    assert blockchain_monitor_original.can_process_transactions(transactions) is True

@pytest.mark.asyncio
async def test_empty_block(mock_w3_original):
    """Test handling of empty blocks"""
    monitor = BlockchainMonitor(mock_w3_original)
    mock_w3_original.eth.get_block.return_value = {'transactions': [], 'number': 12345}
    response = await monitor.process_block(12345)
    assert response['status'] == 'success'
    assert len(response.get('transactions', [])) == 0

@pytest.mark.asyncio
async def test_malformed_transaction(mock_w3_original):
    """Test handling of malformed transaction data"""
    monitor = BlockchainMonitor(mock_w3_original)
    mock_w3_original.eth.get_transaction.return_value = {'hash': '0x1234', 'value': None}
    response = await monitor.verify_transaction('0x1234')
    assert response['status'] == 'error'
    assert 'invalid transaction data' in response['message'].lower()

def test_extreme_gas_prices(blockchain_monitor_original):
    """Test handling of extreme gas prices"""
    test_cases = [
        (0, True),
        (1_000_000_000_000_000, False),
        (10, True)
    ]

    for price, expected in test_cases:
        blockchain_monitor_original.w3.eth.gas_price = price
        assert blockchain_monitor_original.is_gas_price_acceptable() == expected

@pytest.mark.asyncio
async def test_network_timeout(mock_w3_original):
    """Test handling of network timeouts"""
    monitor = BlockchainMonitor(mock_w3_original)
    mock_w3_original.eth.get_block.side_effect = TimeoutError("Request timed out")
    response = await monitor.process_block(12345)
    assert response['status'] == 'error'
    assert 'timeout' in response['message'].lower()

def test_monitor_transaction(blockchain_monitor_original):
    tx_data = {
        'type': 'gold_transformation',
        'status': 'success',
        'tx_hash': '0x123'
    }
    result = blockchain_monitor_original.monitor_transactions(tx_data)
    assert result['status'] == 'monitored'

def test_alert_system(blockchain_monitor_original):
    result = blockchain_monitor_original.send_alert("Test alert")
    assert result['status'] == 'sent'

def test_block_monitoring(blockchain_monitor_original, mock_w3_original):
    mock_w3_original.eth.get_block_number.return_value = 1001
    assert blockchain_monitor_original.check_new_blocks()

from decimal import Decimal
from web3 import Web3
from web3.exceptions import TransactionNotFound