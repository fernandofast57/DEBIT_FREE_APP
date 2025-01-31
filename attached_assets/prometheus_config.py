
from prometheus_client import Counter, Summary, Gauge
from functools import wraps
import time

# Metriche per la distribuzione settimanale dell'oro
GOLD_DISTRIBUTION_DURATION = Summary(
    'gold_distribution_process_duration_seconds',
    'Time spent processing weekly gold distribution')

GOLD_DISTRIBUTION_TOTAL = Counter(
    'gold_distribution_total', 'Total number of gold distributions processed')

GOLD_DISTRIBUTION_ERRORS = Counter(
    'gold_distribution_errors_total',
    'Number of errors during gold distribution', ['error_type'])

GOLD_AMOUNT_PROCESSED = Gauge('gold_amount_processed_grams',
                              'Amount of gold processed in grams')

EURO_AMOUNT_PROCESSED = Gauge('euro_amount_processed',
                              'Amount of euros processed')

ACTIVE_DISTRIBUTIONS = Gauge('gold_distribution_active',
                             'Number of active distribution processes')

def track_distribution_metrics(func):
    """Decorator per tracciare le metriche della distribuzione"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        ACTIVE_DISTRIBUTIONS.inc()
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)

            # Aggiorna le metriche
            GOLD_DISTRIBUTION_DURATION.observe(time.time() - start_time)
            GOLD_DISTRIBUTION_TOTAL.inc()

            if 'total_gold' in result:
                GOLD_AMOUNT_PROCESSED.set(float(result['total_gold']))
            if 'total_euro' in result:
                EURO_AMOUNT_PROCESSED.set(float(result['total_euro']))

            return result

        except Exception as e:
            GOLD_DISTRIBUTION_ERRORS.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            ACTIVE_DISTRIBUTIONS.dec()

    return wrapper
