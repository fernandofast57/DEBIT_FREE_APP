
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def monitor_async_operations(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except RuntimeWarning as w:
            if "coroutine was never awaited" in str(w):
                logger.critical(f"Async operation not properly awaited in {func.__name__}")
                raise RuntimeError(f"Async operation error in {func.__name__}: {str(w)}")
        except Exception as e:
            logger.error(f"Error in async operation {func.__name__}: {str(e)}")
            raise
    return wrapper
