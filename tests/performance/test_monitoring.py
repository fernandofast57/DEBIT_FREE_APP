
import pytest
from app.utils.monitoring import monitor_performance
from app.utils.system_monitor import SystemMonitor
from app.utils.performance_monitor import PerformanceMonitor

def test_system_monitoring():
    """Test system monitoring capabilities"""
    monitor = SystemMonitor()
    
    # Test monitoring functions
    monitor.log_request('/api/test')
    monitor.log_error('test_error')
    monitor.log_response_time(0.5)
    
    assert monitor.get_average_response_time() > 0
    assert monitor.metrics['endpoint_usage']['/api/test'] == 1
    assert monitor.metrics['error_counts']['test_error'] == 1

def test_performance_monitor():
    """Test performance monitoring capabilities"""
    monitor = PerformanceMonitor()
    monitor.record_metric('test_category', 1.5)
    
    metrics = monitor.get_metrics()
    assert 'test_category' in metrics
    assert len(metrics['test_category']) == 1
    assert metrics['test_category'][0] == 1.5

@monitor_performance
def test_performance_decorator():
    """Test performance monitoring decorator"""
    # Simulate some work
    result = sum(range(1000))
    assert result == 499500  # Validate actual computation
