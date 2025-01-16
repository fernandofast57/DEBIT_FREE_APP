
import logging
import time
from functools import wraps
from typing import Callable, Any, Dict, List, Set

logger = logging.getLogger(__name__)

def monitor_performance(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 5.0:  # Alert on slow operations
                logger.warning(f"Performance Alert: {func.__name__} took {execution_time:.2f} seconds")
                
            logger.info(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Critical Error in {func.__name__}: {str(e)}")
            # Notify administrators
            await notify_admin(func.__name__, str(e))
            raise
    return wrapper

async def notify_admin(function_name: str, error_details: str):
    """Notifica gli amministratori in caso di errori critici"""
    logger.critical(f"Admin Alert - Function: {function_name}, Error: {error_details}")
    # Implementa qui la logica di notifica (email, SMS, etc.)

class SystemMonitor:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'error_counts': {},
            'endpoint_usage': {},
            'active_users': set()
        }
    
    def log_request(self, endpoint: str):
        if endpoint not in self.metrics['endpoint_usage']:
            self.metrics['endpoint_usage'][endpoint] = 0
        self.metrics['endpoint_usage'][endpoint] += 1
    
    def log_error(self, error_type: str):
        if error_type not in self.metrics['error_counts']:
            self.metrics['error_counts'][error_type] = 0
        self.metrics['error_counts'][error_type] += 1
    
    def log_response_time(self, time: float):
        self.metrics['response_times'].append(time)
    
    def get_average_response_time(self) -> float:
        if not self.metrics['response_times']:
            return 0.0
        return sum(self.metrics['response_times']) / len(self.metrics['response_times'])
