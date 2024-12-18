
from functools import wraps
import logging
import time
from typing import Callable, Any

def retry_with_fallback(func: Callable) -> Callable:
    """Decorator that retries a function with exponential backoff"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        max_attempts = 3
        attempt = 0
        backoff = 1
        
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt == max_attempts:
                    raise e
                
                logging.warning(f"Attempt {attempt} failed: {str(e)}. Retrying in {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                
    return wrapper
