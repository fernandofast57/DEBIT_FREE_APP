
import time
from collections import defaultdict
from typing import Dict, Tuple

class RobustRateLimiter:
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url
        self.local_storage: Dict[str, Dict[str, Tuple[int, float]]] = defaultdict(dict)
        
    def is_rate_limited(self, key: str, max_requests: int = 100, window: int = 60) -> bool:
        current = time.time()
        
        if key not in self.local_storage:
            self.local_storage[key] = {'count': 1, 'window_start': current}
            return False
            
        window_start = self.local_storage[key]['window_start']
        if current - window_start > window:
            self.local_storage[key] = {'count': 1, 'window_start': current}
            return False
            
        self.local_storage[key]['count'] += 1
        return self.local_storage[key]['count'] > max_requests
