
from dataclasses import dataclass
import time
from typing import Dict
from collections import defaultdict

@dataclass
class RateLimit:
    requests: int
    window: int
    max_requests: int = None
    window_size: int = None

    def __post_init__(self):
        self.max_requests = self.max_requests or self.requests
        self.window_size = self.window_size or self.window

class RobustRateLimiter:
    def __init__(self):
        self.local_storage: Dict[str, Dict] = defaultdict(dict)
        self.window_size = 60  # 1 minute window
        self.max_requests = 50  # 50 requests per minute

    def is_rate_limited(self, key: str, max_requests: int = None, window_size: int = None) -> bool:
        current = time.time()
        window_size = window_size or self.window_size
        max_reqs = max_requests or self.max_requests
        
        if key not in self.local_storage:
            self.local_storage[key] = {'count': 1, 'window_start': current}
            return False
            
        window_start = self.local_storage[key]['window_start']
        if current - window_start > window_size:
            self.local_storage[key] = {'count': 1, 'window_start': current}
            return False
            
        self.local_storage[key]['count'] += 1
        return self.local_storage[key]['count'] > max_reqs
