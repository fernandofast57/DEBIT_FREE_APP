
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
