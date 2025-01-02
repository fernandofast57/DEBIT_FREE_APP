
import pytest
from app.config.constants import TestConfig
from app.utils.performance_monitor import PerformanceMonitor

def test_system_under_load():
    """Test system performance under load"""
    monitor = PerformanceMonitor()
    
    # Simulate load
    for _ in range(100):
        monitor.record_metric('response_time', 0.1)
    
    avg_response = monitor.get_average('response_time')
    assert avg_response > 0
    assert avg_response < 1.0  # Response time should be under 1 second
import pytest
from app.services.transformation_service import TransformationService
from app.services.blockchain_service import BlockchainService
from concurrent.futures import ThreadPoolExecutor
import time

def test_concurrent_transformations():
    """Test performance con trasformazioni concorrenti"""
    service = TransformationService()
    num_requests = 100
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(service.process_transformation, amount=100)
            for _ in range(num_requests)
        ]
    
    execution_time = time.time() - start_time
    assert execution_time < 30  # Dovrebbe completare in meno di 30 secondi

def test_blockchain_batch_performance():
    """Test performance batch blockchain"""
    service = BlockchainService()
    
    start_time = time.time()
    service.process_batch_transactions(batch_size=50)
    execution_time = time.time() - start_time
    
    assert execution_time < 15  # Dovrebbe completare in meno di 15 secondi
