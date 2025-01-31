import pytest
from datetime import datetime
from app.utils.monitoring.performance_monitor import SystemPerformanceMonitor

@pytest.fixture
def performance_monitor():
    return SystemPerformanceMonitor()

def test_metric_recording(performance_monitor):
    performance_monitor.record_metric('response_time', 100.0)
    metrics = performance_monitor.get_metrics()
    assert 'response_time' in metrics
    assert metrics['response_time']['count'] == 1

def test_alert_threshold(performance_monitor):
    performance_monitor.record_metric('cpu_usage', 95.0)  # Above typical threshold
    alerts = performance_monitor.get_alerts()
    assert len(alerts) > 0
    assert 'cpu_usage' in alerts[0]['metric']

def test_metrics_cleanup(performance_monitor):
    performance_monitor.record_metric('memory_usage', 75.0)
    performance_monitor.cleanup_old_metrics()
    metrics = performance_monitor.get_metrics()
    assert 'memory_usage' in metrics

def test_multiple_metrics(performance_monitor):
    metrics = {
        'cpu_usage': 60.0,
        'memory_usage': 512.0,
        'network_latency': 50.0
    }
    for metric_type, value in metrics.items():
        performance_monitor.record_metric(metric_type, value)

    recorded_metrics = performance_monitor.get_metrics()
    for metric_type in metrics:
        assert metric_type in recorded_metrics


def test_report_format(performance_monitor):
    report = performance_monitor.get_report()
    assert 'timestamp' in report
    assert 'metrics' in report
    assert 'alerts' in report # Added based on the context of the edited code