import asyncio
from flask import Flask
import logging
from typing import Dict, Any
from app.utils.monitoring.performance_monitor import PerformanceMonitor
from app.utils.system_monitor import SystemMonitor

logger = logging.getLogger(__name__)
performance_monitor = PerformanceMonitor()
system_monitor = SystemMonitor()

def setup_monitoring(app: Flask) -> None:
    """Setup monitoring for the application"""

    @app.before_request
    def before_request():
        performance_monitor.start_request()

    @app.after_request
    def after_request(response):
        performance_monitor.end_request()
        metrics = system_monitor.collect_metrics()
        if metrics.get('cpu_percent', 0) > 80:
            logger.warning(f"High CPU usage detected: {metrics['cpu_percent']}%")
        return response

    app.logger.info("Monitoring has been set up")