import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

class DeviceConfig:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.last_rotation = datetime.now()
        self.max_requests = 1000
        self.window_size = 3600  # 1 hour in seconds

class AdvancedConfig:
    def __init__(self):
        self.logger = logging.getLogger('advanced_config')
        self.devices: Dict[str, DeviceConfig] = {}
        self.rotation_interval = timedelta(days=1)

    def get_device_config(self, device_id: str) -> DeviceConfig:
        if device_id not in self.devices:
            self.devices[device_id] = DeviceConfig(device_id)
        return self.devices[device_id]

    def check_secrets_rotation(self):
        """Check if secrets need rotation"""
        for device in self.devices.values():
            if datetime.now() - device.last_rotation > self.rotation_interval:
                self.logger.info(f"Rotating secrets for device {device.device_id}")
                device.last_rotation = datetime.now()