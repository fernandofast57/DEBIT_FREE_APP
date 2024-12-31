
import pytest
from web3 import Web3
from app.utils.blockchain_monitor import BlockchainMonitor
from datetime import datetime

@pytest.fixture
def web3_mock():
    w3 = Web3()
    w3.eth.gas_price = 50_000_000_000  # 50 gwei
    return w3

@pytest.fixture
def monitor(web3_mock):
    return BlockchainMonitor(web3_mock)

def test_monitor_transaction_success(monitor):
    transaction_data = {
        'type': 'transfer',
        'status': 'success',
        'tx_hash': '0x123'
    }
    
    monitor.monitor_transactions(transaction_data)
    metrics = monitor.get_metrics()
    
    assert len(metrics['transactions']) == 1
    assert metrics['transactions'][0]['type'] == 'transfer'
    assert metrics['transactions'][0]['status'] == 'success'
    assert metrics['transactions'][0]['tx_hash'] == '0x123'

def test_monitor_high_gas_alert(monitor, caplog):
    monitor.w3.eth.gas_price = 150_000_000_000  # 150 gwei
    
    transaction_data = {
        'type': 'transfer',
        'status': 'pending'
    }
    
    monitor.monitor_transactions(transaction_data)
    assert any("High gas price detected" in record.message for record in caplog.records)

def test_metrics_limit(monitor):
    for i in range(150):
        monitor.monitor_transactions({
            'type': 'test',
            'status': 'success',
            'tx_hash': f'0x{i}'
        })
    
    metrics = monitor.get_metrics()
    assert len(metrics['transactions']) == 100  # Verifica che mantenga solo gli ultimi 100
