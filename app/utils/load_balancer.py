
from flask import current_app
import logging
from typing import List, Dict
import random

logger = logging.getLogger(__name__)

class LoadBalancer:
    def __init__(self):
        self.servers: List[Dict] = []
        self.current_index = 0
        
    def register_server(self, host: str, port: int, weight: int = 1):
        """Register a new server in the load balancer pool"""
        server = {
            'host': host,
            'port': port,
            'weight': weight,
            'active': True,
            'current_load': 0
        }
        self.servers.append(server)
        logger.info(f"Registered new server: {host}:{port}")
        
    def get_next_server(self) -> Dict:
        """Get next available server using round-robin algorithm"""
        if not self.servers:
            raise Exception("No servers available")
            
        # Simple round-robin implementation
        available = [s for s in self.servers if s['active'] and s['current_load'] < 100]
        if not available:
            raise Exception("No servers available with capacity")
            
        server = available[self.current_index % len(available)]
        self.current_index += 1
        return server
        
    def update_server_load(self, host: str, port: int, load: int):
        """Update current load for a server"""
        for server in self.servers:
            if server['host'] == host and server['port'] == port:
                server['current_load'] = load
                break

load_balancer = LoadBalancer()
# Register default server
load_balancer.register_server(host='0.0.0.0', port=8080)
