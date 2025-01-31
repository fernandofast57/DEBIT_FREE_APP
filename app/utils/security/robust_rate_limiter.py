import time
from typing import Dict, Tuple
from collections import defaultdict
import threading

class RobustRateLimiter:
    def __init__(self, limit: int = 100, window: int = 60):
        self.limit = limit  # Max requests per window
        self.window = window  # Window in seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        with self.lock:
            now = time.time()
            key_requests = self.requests[key]

            # Remove old requests
            while key_requests and key_requests[0] < now - self.window:
                key_requests.pop(0)

            # Check if limit is reached
            if len(key_requests) >= self.limit:
                return False

            # Add new request
            key_requests.append(now)
            return True

rate_limit = RobustRateLimiter()