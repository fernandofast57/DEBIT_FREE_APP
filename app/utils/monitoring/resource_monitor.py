import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

class MonitorRisorse:
    def __init__(self):
        self.resources = {}
        self.usage_history = {}
        
    def track_resource_usage(self, resource_name: str, usage: float) -> None:
        timestamp = time.time()
        if resource_name not in self.usage_history:
            self.usage_history[resource_name] = []
            
        self.usage_history[resource_name].append({
            'timestamp': timestamp,
            'usage': usage
        })
        
        # Keep only last 24 hours of data
        cutoff = timestamp - (24 * 3600)
        self.usage_history[resource_name] = [
            entry for entry in self.usage_history[resource_name] 
            if entry['timestamp'] > cutoff
        ]