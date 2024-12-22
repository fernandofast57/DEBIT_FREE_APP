
from collections import defaultdict
import time
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self._requests = defaultdict(list)
        self._ip_tracking = defaultdict(int)
        self._max_requests = 100
        self._window = 3600  # 1 hour window
        self._ip_threshold = 1000  # Max requests per IP
        
    def is_allowed(self, user_id: str, ip_address: str) -> bool:
        now = time.time()
        self._cleanup_old_requests(now)
        
        # Check IP limits
        if self._ip_tracking[ip_address] > self._ip_threshold:
            logger.warning(f"IP {ip_address} exceeded threshold")
            return False
            
        # Check user limits
        user_requests = self._requests[user_id]
        if len(user_requests) < self._max_requests:
            user_requests.append(now)
            self._ip_tracking[ip_address] += 1
            return True
            
        return False
        
    def _cleanup_old_requests(self, now: float):
        cutoff = now - self._window
        for user_id in list(self._requests.keys()):
            self._requests[user_id] = [t for t in self._requests[user_id] if t > cutoff]
