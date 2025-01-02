
import pytest
from web3 import Web3
from datetime import datetime
from unittest.mock import Mock
from app.utils.blockchain_monitor import BlockchainMonitor

@pytest.fixture
def web3_mock():
    w3 = Mock()
    w3.eth.gas_price = 50_000_000_000  # 50 gwei
    w3.eth.chain_id = 1
    return w3

@pytest.fixture
def monitor(web3_mock):
    return BlockchainMonitor(web3_mock)

def test_monitor_transaction_success(monitor):
    transaction_data = {
        'type': 'transfer',
        'status': 'success',
        'tx_hash': '0x123',
        'block_number': 100
    }
    
    monitor.monitor_transactions(transaction_data)
    metrics = monitor.get_metrics()
    
    assert len(metrics['transactions']) == 1
    assert metrics['transactions'][0]['type'] == 'transfer'
    assert metrics['transactions'][0]['status'] == 'success'
    assert metrics['transactions'][0]['tx_hash'] == '0x123'

@pytest.mark.asyncio
async def test_monitor_network(monitor, web3_mock):
    web3_mock.net.peer_count = 3
    web3_mock.net.listening = True
    
    await monitor.monitor_network()
    metrics = monitor.get_metrics()
    
    assert metrics['network_stats']['peer_count'] == 3
    assert metrics['network_stats']['is_listening'] == True
    assert metrics['network_stats']['network_id'] == 1

@pytest.mark.asyncio
async def test_monitor_block_time(monitor, web3_mock):
    web3_mock.eth.block_number = 100
    web3_mock.eth.get_block.side_effect = [
        {'timestamp': 1600000000},
        {'timestamp': 1599999970}
    ]
    
    await monitor.monitor_block_time()
    metrics = monitor.get_metrics()
    
    assert len(metrics['block_times']) == 1
    assert metrics['block_times'][0]['block_time'] == 30
    assert metrics['block_times'][0]['block_number'] == 100

def test_metrics_limit(monitor):
    for i in range(150):
        monitor.monitor_transactions({
            'type': 'test',
            'status': 'success',
            'tx_hash': f'0x{i}',
            'block_number': i
        })
    metrics = monitor.get_metrics()
    assert len(metrics['transactions']) == 100  # Verifica limite di ritenzione
@pytest.mark.asyncio
async def test_reconnection_system(blockchain_service):
    """Test automatic reconnection system"""
    # Simulate connection drop
    blockchain_service.w3.is_connected.return_value = False
    
    # Force reconnection attempt
    await blockchain_service._connect_to_rpc()
    
    # Verify multiple connection attempts were made
    assert blockchain_service.w3.is_connected.call_count > 1
    assert blockchain_service.current_rpc_index == 0  # Should reset to first endpoint
