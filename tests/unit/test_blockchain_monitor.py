
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
