import asyncio
from flask import Flask, request
import logging
from datetime import datetime
from typing import Dict, Any
from ..cache.redis_manager import cache_manager
from .performance_metrics import metrics_collector  # <-- IMPORTAZIONE CORRETTA: metrics_collector

logger = logging.getLogger(__name__)


def setup_monitoring(app: Flask) -> None:
    """Initialize standard system monitoring"""

    @app.before_request
    async def initialize_request_monitoring():
        request.start_timestamp = datetime.utcnow()
        request.monitoring_context = {
            'start_time': datetime.utcnow(),
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path
        }
        await metrics_collector.collect_system_metrics(
        )  # <-- USO CORRETTO: metrics_collector

    @app.after_request
    async def finalize_request_monitoring(response):
        execution_time = (datetime.utcnow() -
                          request.start_timestamp).total_seconds() * 1000
        await metrics_collector.record_metric(
            'response_time_ms',
            execution_time)  # <-- USO CORRETTO: metrics_collector
        return response

    logger.info("Monitoring setup completed")
