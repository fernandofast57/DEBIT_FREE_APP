# prometheus_config.py
from prometheus_client import Counter, Histogram
import time

# Metriche per il monitoraggio
REQUEST_COUNT = Counter('request_count', 'Total request count',
                        ['method', 'endpoint', 'status'])

REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency',
                            ['endpoint'])

DB_QUERY_LATENCY = Histogram('db_query_latency_seconds',
                             'Database query latency', ['query_type'])


def track_request(fn):
    """Decorator per tracciare le richieste"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        response = fn(*args, **kwargs)
        latency = time.time() - start_time

        REQUEST_COUNT.labels(method=request.method,
                             endpoint=request.endpoint,
                             status=response.status_code).inc()

        REQUEST_LATENCY.labels(endpoint=request.endpoint).observe(latency)

        return response

    return wrapper
