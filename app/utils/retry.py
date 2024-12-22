
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=3, initial_delay=1, max_delay=60, exponential_base=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        sleep_time = min(delay * (exponential_base ** attempt), max_delay)
                        time.sleep(sleep_time)
            
            logger.error(f"All {max_retries} attempts failed")
            raise last_exception
            
        return wrapper
    return decorator
