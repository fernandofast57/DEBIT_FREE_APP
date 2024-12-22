
import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(
    retries: int = 3,
    backoff_in_seconds: int = 1,
    max_backoff_in_seconds: int = 60
) -> Callable:
    def decorator(operation: Callable) -> Callable:
        @wraps(operation)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(retries):
                try:
                    return await operation(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == retries - 1:
                        raise
                    sleep_time = min(
                        max_backoff_in_seconds,
                        backoff_in_seconds * (2 ** attempt)
                    )
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {sleep_time} seconds..."
                    )
                    time.sleep(sleep_time)
            raise last_exception
        return wrapper
    return decorator
