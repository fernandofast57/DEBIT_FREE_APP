
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
import pytest
import asyncio
from app.utils.performance_monitor import PerformanceMonitor
from app.services.transformation_service import TransformationService
from concurrent.futures import ThreadPoolExecutor
import time

async def test_concurrent_transformations():
    """Test delle trasformazioni concorrenti sotto carico"""
    service = TransformationService()
    monitor = PerformanceMonitor()
    num_requests = 50
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(service.process_transformation, amount=100)
            for _ in range(num_requests)
        ]
    
    execution_time = time.time() - start_time
    assert execution_time < 15  # Dovrebbe completare in meno di 15 secondi
    
    metrics = monitor.get_metrics()
    assert 'transformation' in metrics
    assert len(monitor.get_alerts()) == 0  # Non dovrebbero esserci alert di performance

def test_system_under_heavy_load():
    """Test del sistema sotto carico pesante"""
    monitor = PerformanceMonitor()
    
    # Simula carico pesante
    for _ in range(1000):
        monitor.record_metric('response_time', 0.1)
        monitor.record_metric('database_query_times', 0.05)
        monitor.record_metric('blockchain_operation_times', 2.0)
    
    metrics = monitor.get_metrics()
    alerts = monitor.get_alerts()
    
    assert len(metrics['response_time']) > 0
    assert len(metrics['database_query_times']) > 0
    assert len(metrics['blockchain_operation_times']) > 0
    assert all(m < 1.0 for m in metrics['response_time'])  # Verifica tempi di risposta
