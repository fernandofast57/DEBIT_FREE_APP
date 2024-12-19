
from collections import defaultdict
import time
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        self._requests = defaultdict(list)
        self._max_requests = 100
        self._window = 3600  # 1 hour window
        
    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        user_requests = self._requests[user_id]
        
        # Remove old requests
        while user_requests and user_requests[0] < now - self._window:
            user_requests.pop(0)
            
        # Check if under limit
        if len(user_requests) < self._max_requests:
            user_requests.append(now)
            return True
            
        return False
