
import time
import logging
from functools import wraps
from flask import request, g

logger = logging.getLogger(__name__)

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        result = f(*args, **kwargs)
        
        duration = time.time() - start_time
        logger.info(f"Route {request.path} took {duration:.2f} seconds")
        
        if duration > 1.0:
            logger.warning(f"Slow request detected: {request.path} took {duration:.2f} seconds")
        
        return result
    return decorated_function
