
import pytest
from web3 import Web3
from datetime import datetime
from unittest.mock import Mock, patch
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

def test_monitor_empty_transaction(monitor):
    """Test handling of empty transaction data"""
    empty_data = {}
    monitor.monitor_transactions(empty_data)
    metrics = monitor.get_metrics()
    
    assert len(metrics['transactions']) == 1
    assert metrics['transactions'][0]['type'] == 'unknown'
    assert metrics['transactions'][0]['status'] == 'unknown'

def test_monitor_invalid_gas_price(monitor, web3_mock):
    """Test handling of invalid gas price"""
    web3_mock.eth.gas_price = -1  # Invalid gas price
    transaction_data = {'type': 'transfer'}
    
    monitor.monitor_transactions(transaction_data)
    metrics = monitor.get_metrics()
    
    assert len(metrics['errors']) > 0

def test_monitor_large_number_transactions(monitor):
    """Test handling of many transactions"""
    for i in range(150):  # Test with more transactions than retention limit
        monitor.monitor_transactions({
            'type': 'test',
            'tx_hash': f'0x{i}'
        })
    
    metrics = monitor.get_metrics()
    assert len(metrics['transactions']) <= 100  # Check retention policy

def test_monitor_special_characters(monitor):
    """Test handling of special characters in transaction data"""
    transaction_data = {
        'type': 'transfer!@#$%^',
        'status': 'success\n\t',
        'tx_hash': '0x123'
    }
    
    monitor.monitor_transactions(transaction_data)
    metrics = monitor.get_metrics()
    
    assert len(metrics['transactions']) == 1
    assert isinstance(metrics['transactions'][0]['type'], str)

def test_monitor_concurrent_access(monitor):
    """Test concurrent transaction monitoring"""
    import threading
    
    def add_transactions():
        for i in range(10):
            monitor.monitor_transactions({
                'type': 'test',
                'tx_hash': f'0x{i}'
            })
    
    threads = [threading.Thread(target=add_transactions) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    metrics = monitor.get_metrics()
    assert len(metrics['transactions']) == 50
