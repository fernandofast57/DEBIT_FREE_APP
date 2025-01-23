
from dataclasses import dataclass

@dataclass
class RateLimit:
    requests: int
    window: int
    max_requests: int = None
    window_size: int = None

    def __post_init__(self):
        self.max_requests = self.max_requests or self.requests
        self.window_size = self.window_size or self.window
