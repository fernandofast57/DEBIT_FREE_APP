
import pytest
from flask import Flask
from app.utils.monitoring import SystemMonitor, monitor_performance

def test_system_monitor_initialization():
    monitor = SystemMonitor()
    assert monitor.metrics['response_times'] == []
    assert monitor.metrics['error_counts'] == {}
    assert monitor.metrics['endpoint_usage'] == {}
    assert isinstance(monitor.metrics['active_users'], set)

def test_log_request():
    monitor = SystemMonitor()
    monitor.log_request(endpoint='test')
    assert monitor.metrics['endpoint_usage']['test'] == 1

def test_log_error():
    monitor = SystemMonitor()
    monitor.log_error('ValueError')
    assert monitor.metrics['error_counts']['ValueError'] == 1

def test_response_time_logging():
    monitor = SystemMonitor()
    monitor.log_response_time(0.5)
    assert len(monitor.metrics['response_times']) == 1
    assert monitor.metrics['response_times'][0] == 0.5

def test_average_response_time():
    monitor = SystemMonitor()
    monitor.log_response_time(0.5)
    monitor.log_response_time(1.5)
    assert monitor.get_average_response_time() == 1.0

import time

def test_monitor_performance_decorator():
    app = Flask(__name__)
    monitor = SystemMonitor()
    
    @app.route('/test')
    @monitor_performance
    def test_function():
        time.sleep(0.1)  # Simulate some work
        return "Test Success"
    
    with app.test_client() as client:
        response = client.get('/test')
        assert response.data.decode() == "Test Success"
        assert len(monitor.metrics['response_times']) > 0
        assert monitor.metrics['response_times'][-1] > 0
