import logging

class TokenManager:
    def __init__(self):
        self.tokens = {}
        self.logger = logging.getLogger(__name__)

    def validate_token(self, token: str) -> bool:
        if not token or token not in self.tokens:
            self.logger.warning(f"Invalid token attempted: {token[:10]}...")
            return False
        return True