
from app import create_app
from config import Config
from app.utils.validation_report import ValidationReport
from app.utils.system_monitor import SystemMonitor
from app.utils.monitoring.performance_monitor import PerformanceMonitor
from app.utils.security.circuit_breaker import CircuitBreaker
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_system_check():
    app = create_app(Config)
    with app.app_context():
        # Inizializza i componenti di monitoraggio
        validator = ValidationReport()
        system_monitor = SystemMonitor()
        performance_monitor = PerformanceMonitor()
        circuit_breaker = CircuitBreaker()

        # Genera report completo
        validation_report = await validator.generate_report()
        system_metrics = system_monitor.collect_metrics()
        performance_stats = performance_monitor.get_stats()
        
        print("\n=== System Debug Report ===")
        
        print("\n1. Connessioni:")
        print("Blockchain:", "✓" if validation_report['blockchain'].get('connection') else "✗")
        print("Database:", "✓" if not validation_report.get('database', {}).get('error') else "✗")
        print("Redis Cache:", "✓" if system_metrics.get('redis_connected', False) else "✗")
        
        print("\n2. Performance:")
        print(f"CPU Usage: {system_metrics.get('cpu_percent', 0)}%")
        print(f"Memory Usage: {system_metrics.get('memory_percent', 0)}%")
        print(f"Average Response Time: {performance_stats.get('avg_response_time', 0)}ms")
        
        print("\n3. Sistema Noble:")
        print("Noble System Status:", "✓" if validation_report['structure']['noble_system'] else "✗")
        print("Bonus Distribution:", "✓" if validation_report['structure'].get('bonus_system') else "✗")
        
        print("\n4. Sicurezza:")
        print("Circuit Breaker Status:", "✓" if circuit_breaker.get_status() == 'CLOSED' else "✗")
        print("Rate Limiting:", "✓" if validation_report['security'].get('rate_limiting') else "✗")
        
        print("\nDettagli completi:", validation_report)

if __name__ == "__main__":
    asyncio.run(run_system_check())
