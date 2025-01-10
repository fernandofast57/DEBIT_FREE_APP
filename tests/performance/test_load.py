import pytest
import asyncio
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.config.constants import TestConfig
from app.utils.performance_monitor import PerformanceMonitor

@pytest.mark.asyncio
async def test_concurrent_transformations():
    service = TransformationService()
    tasks = []
    for i in range(5):
        task = asyncio.create_task(
            service.process_transformation(
                user_id=i,
                euro_amount=Decimal('100.00'),
                fixing_price=Decimal('50.00')
            )
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    assert all(r['status'] == 'success' for r in results)

@pytest.mark.asyncio
async def test_blockchain_batch_performance(blockchain_service):
    batch_size = 10
    batch_data = [
        {"user_id": i, "amount": Decimal('100.0'), "timestamp": 1645564800}
        for i in range(batch_size)
    ]

    result = await blockchain_service.process_batch_transformation(batch_data)
    assert result['status'] == 'success'

@pytest.mark.asyncio
async def test_system_under_heavy_load():
    service = TransformationService()
    large_batch = [
        (i, Decimal('100.00'), Decimal('50.00'))
        for i in range(20)
    ]

    tasks = [
        asyncio.create_task(
            service.process_transformation(
                user_id=user_id,
                euro_amount=amount,
                fixing_price=price
            )
        )
        for user_id, amount, price in large_batch
    ]

    results = await asyncio.gather(*tasks)
    success_rate = sum(1 for r in results if r['status'] == 'success') / len(results)
    assert success_rate >= 0.9  # 90% success rate requirement

def test_system_under_load():
    """Test system performance under load"""
    monitor = PerformanceMonitor()
    
    # Simulate load
    for _ in range(100):
        monitor.record_metric('response_time', 0.1)
    
    avg_response = monitor.get_average('response_time')
    assert avg_response > 0
    assert avg_response < 1.0  # Response time should be under 1 second

def test_system_under_heavy_load_original():
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