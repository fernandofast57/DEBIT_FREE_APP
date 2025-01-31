
import time
import logging
from collections import defaultdict
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._blocked: Dict[str, datetime] = {}

    def is_allowed(self, key: str, max_requests: int, window_size: int) -> bool:
        now = time.time()
        
        # Check if key is blocked
        if self._is_blocked(key):
            return False

        # Clean old requests
        self._clean_old_requests(key, window_size)
        
        # Check rate limit
        if len(self._requests[key]) >= max_requests:
            self._block_key(key)
            logger.warning(f"Rate limit exceeded for {key}")
            return False

        self._requests[key].append(now)
        return True

    def _is_blocked(self, key: str) -> bool:
        if key in self._blocked:
            if datetime.now() > self._blocked[key]:
                del self._blocked[key]
                return False
            return True
        return False

    def _block_key(self, key: str):
        self._blocked[key] = datetime.now().replace(minute=datetime.now().minute + 5)

    def _clean_old_requests(self, key: str, window_size: int):
        now = time.time()
        self._requests[key] = [t for t in self._requests[key] if t > now - window_size]
