class RateLimit:

    def __init__(self, limit: int, interval: int):
        self.limit = limit
        self.interval = interval

    def apply_limit(self, request):
        return f"Applying limit: {self.limit} per {self.interval} seconds"


class RobustRateLimiter:

    def __init__(self, limit: int, interval: int):
        self.rate_limit = RateLimit(limit, interval)

    def check_limit(self, request):
        return self.rate_limit.apply_limit(request)
