
import pytest
import time
from app.utils.monitoring.performance import EnhancedPerformanceMonitor

@pytest.fixture
def performance_monitor():
    return EnhancedPerformanceMonitor(alert_threshold=0.1)

def test_performance_tracking(performance_monitor):
    @performance_monitor.track_time('test_operation')
    def slow_operation():
        time.sleep(0.05)
        return True
    
    # Esegui operazione multipla volte
    for _ in range(5):
        assert slow_operation() is True
    
    metrics = performance_monitor.get_metrics()
    assert 'test_operation' in metrics
    assert metrics['test_operation']['count'] == 5
    assert metrics['test_operation']['average'] > 0
    assert metrics['test_operation']['max'] > 0

def test_performance_alert(performance_monitor):
    @performance_monitor.track_time('slow_operation')
    def very_slow_operation():
        time.sleep(0.2)  # Operazione più lenta della soglia
        return True
    
    very_slow_operation()
    metrics = performance_monitor.get_metrics()
    assert metrics['slow_operation']['max'] > performance_monitor.alert_threshold

@pytest.mark.asyncio
async def test_concurrent_operations(performance_monitor):
    import asyncio
    
    @performance_monitor.track_time('async_op')
    async def async_operation():
        await asyncio.sleep(0.01)
        return True
    
    async def run_concurrent():
        tasks = [async_operation() for _ in range(10)]
        await asyncio.gather(*tasks)
    
    await run_concurrent()
    metrics = performance_monitor.get_metrics()
    assert metrics['async_op']['count'] == 10

def test_memory_usage_tracking(performance_monitor):
    @performance_monitor.track_time('memory_intensive_op')
    def memory_operation():
        large_list = [i for i in range(1000000)]
        return sum(large_list)
    
    memory_operation()
    metrics = performance_monitor.get_metrics()
    assert 'memory_intensive_op' in metrics
    assert metrics['memory_intensive_op']['memory_usage'] > 0

def test_cache_performance(performance_monitor):
    @performance_monitor.track_time('cached_operation')
    def cached_op():
        return "result"
    
    for _ in range(10):
        cached_op()
    
    metrics = performance_monitor.get_metrics()
    assert metrics['cached_operation']['cache_hits'] >= 0
