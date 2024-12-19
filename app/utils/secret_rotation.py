
import os
import time
from datetime import datetime, timedelta
import logging
from typing import Dict

class SecretRotator:
    def __init__(self, rotation_interval_days: int = 30):
        self.rotation_interval = timedelta(days=rotation_interval_days)
        self.logger = logging.getLogger('secret_rotator')
        self.last_rotation_file = 'logs/last_rotation.txt'
        
    def needs_rotation(self) -> bool:
        if not os.path.exists(self.last_rotation_file):
            return True
            
        with open(self.last_rotation_file, 'r') as f:
            last_rotation = datetime.fromtimestamp(float(f.read().strip()))
            
        return datetime.now() - last_rotation >= self.rotation_interval
        
    def rotate_secrets(self) -> Dict[str, str]:
        """Generate new secrets and update the environment"""
        from secrets import token_hex
        
        new_secrets = {
            'SECRET_KEY': token_hex(32),
            # Add other secrets that need rotation
        }
        
        # Update environment variables
        for key, value in new_secrets.items():
            os.environ[key] = value
            
        # Record rotation time
        with open(self.last_rotation_file, 'w') as f:
            f.write(str(time.time()))
            
        self.logger.info("Secrets rotated successfully")
        return new_secrets
