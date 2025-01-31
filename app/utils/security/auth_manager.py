import logging

class AuthManager:
    def __init__(self):
        self.sessions = {}
        self._active = True
        self.logger = logging.getLogger(__name__)