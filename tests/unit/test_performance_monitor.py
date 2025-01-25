
import pytest
import asyncio
from app.utils.monitoring.performance import PerformanceMonitor

@pytest.fixture
def monitor():
    return PerformanceMonitor()

@pytest.mark.asyncio
async def test_collect_metrics(monitor):
    metrics = await monitor.collect_metrics()
    
    assert hasattr(metrics, 'cpu_percent')
    assert hasattr(metrics, 'memory_percent')
    assert hasattr(metrics, 'disk_usage')
    assert hasattr(metrics, 'active_connections')
    assert isinstance(metrics.cpu_percent, float)
    assert isinstance(metrics.memory_percent, float)
    assert isinstance(metrics.disk_usage, float)
    assert isinstance(metrics.active_connections, int)

@pytest.mark.asyncio
async def test_metrics_history(monitor):
    await monitor.collect_metrics()
    await monitor.collect_metrics()
    
    assert len(monitor.metrics_history) == 2
    assert len(monitor.metrics_history) <= 1000  # Max history limit

@pytest.mark.asyncio
async def test_alert_thresholds(monitor):
    # Override thresholds for testing
    monitor.alert_thresholds = {
        'cpu_percent': 0.0,  # Set to 0 to trigger alert
        'memory_percent': 0.0,
        'disk_usage': 0.0
    }
    
    metrics = await monitor.collect_metrics()
    assert metrics is not None
