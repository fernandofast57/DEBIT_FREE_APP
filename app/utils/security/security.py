
from flask import request
from functools import wraps
import re

class SecurityManager:
    def __init__(self):
        self.max_requests = 100
        self.time_window = 60  # seconds

    @staticmethod
    def validate_address(address):
        """Validate Ethereum address format"""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return False
        return True

    @staticmethod
    def sanitize_input(data):
        """Sanitize user input"""
        if isinstance(data, str):
            return data.strip()
        return data
