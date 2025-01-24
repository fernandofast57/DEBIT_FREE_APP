
import asyncio
from flask import Flask, request
import logging
from datetime import datetime
from typing import Dict, Any
from app.utils.monitoring.performance_monitor import PerformanceMonitor
from app.utils.system_monitor import SystemMonitor
from app.utils.load_balancer import load_balancer
from app.utils.cache.redis_manager import cache_manager

logger = logging.getLogger(__name__)
performance_monitor = PerformanceMonitor()
system_monitor = SystemMonitor()

def setup_monitoring(app: Flask) -> None:
    @app.before_request
    async def before_request():
        request.start_time = datetime.now()
        await performance_monitor.start_request()
        
        # Cache delle richieste frequenti
        if request.method == 'GET':
            cache_key = f"cache:{request.path}:{request.query_string.decode()}"
            cached_response = await cache_manager.get(cache_key)
            if cached_response:
                return cached_response

    @app.after_request
    async def after_request(response):
        # Monitoraggio performance
        request_time = (datetime.now() - request.start_time).total_seconds()
        await performance_monitor.end_request(request_time)
        
        # Cache delle risposte GET
        if request.method == 'GET' and response.status_code == 200:
            cache_key = f"cache:{request.path}:{request.query_string.decode()}"
            await cache_manager.set(cache_key, response, ttl=300)  # 5 minuti
            
        # Metriche sistema
        metrics = await system_monitor.collect_metrics()
        if metrics.get('cpu_percent', 0) > 80:
            logger.warning(f"High CPU usage detected: {metrics['cpu_percent']}%")
            
        # Metriche load balancer
        lb_metrics = await load_balancer.get_metrics()
        logger.info(f"Load balancer metrics: {lb_metrics}")
        
        return response

    logger.info("Enhanced monitoring system has been set up")

    # Avvia health check in background
    asyncio.create_task(load_balancer.update_health_status())
