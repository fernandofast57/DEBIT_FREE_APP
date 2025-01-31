
import pytest
from datetime import datetime, timedelta
from app.utils.monitoring.performance_metrics import StandardPerformanceCollector

@pytest.fixture
def performance_collector():
    return StandardPerformanceCollector()

def test_metric_recording(performance_collector):
    """Test basic metric recording"""
    performance_collector.record_metric('response_time', 100.0)
    performance_collector.record_metric('memory_usage', 50.0)
    report = performance_collector.get_performance_report()
    assert 'response_time' in report['metrics']
    assert 'memory_usage' in report['metrics']

def test_alerts_generation(performance_collector):
    """Test alert generation for threshold violations"""
    performance_collector.record_metric('response_time', 2000.0)  # Above threshold
    report = performance_collector.get_performance_report()
    assert len(report['recent_alerts']) > 0

def test_metrics_cleanup(performance_collector):
    """Test old metrics cleanup"""
    performance_collector.record_metric('cpu_usage', 75.0)
    performance_collector._last_cleanup = datetime.utcnow() - timedelta(hours=2)
    performance_collector._cleanup_old_metrics()
    report = performance_collector.get_performance_report()
    assert 'cpu_usage' in report['metrics']

def test_aggregated_metrics(performance_collector):
    """Test metrics aggregation"""
    for _ in range(3):
        performance_collector.record_metric('response_time', 100.0)
    report = performance_collector.get_performance_report()
    assert report['metrics']['response_time']['average'] == 100.0
