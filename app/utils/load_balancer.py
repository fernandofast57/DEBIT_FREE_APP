
import random
import logging
from typing import Dict, List, Optional
import aiohttp
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LoadBalancer:
    def __init__(self):
        self.servers: List[Dict] = []
        self.health_checks: Dict = {}
        self.last_used_index = -1
        
    def register_server(self, host: str, port: int):
        server = {
            'host': host,
            'port': port,
            'healthy': True,
            'load': 0,
            'last_check': datetime.now()
        }
        self.servers.append(server)
        logger.info(f"Registered new server {host}:{port}")

    async def health_check(self, server: Dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{server['host']}:{server['port']}/health"
                async with session.get(url, timeout=2) as response:
                    return response.status == 200
        except:
            return False

    async def update_health_status(self):
        while True:
            for server in self.servers:
                server['healthy'] = await self.health_check(server)
                server['last_check'] = datetime.now()
            await asyncio.sleep(30)

    def get_next_server(self) -> Optional[Dict]:
        healthy_servers = [s for s in self.servers if s['healthy']]
        if not healthy_servers:
            return None
            
        # Round-robin con considerazione del carico
        min_load = min(s['load'] for s in healthy_servers)
        candidates = [s for s in healthy_servers if s['load'] == min_load]
        
        self.last_used_index = (self.last_used_index + 1) % len(candidates)
        selected_server = candidates[self.last_used_index]
        selected_server['load'] += 1
        
        return selected_server

    def release_server(self, server: Dict):
        if server and server in self.servers:
            server['load'] = max(0, server['load'] - 1)

load_balancer = LoadBalancer()
# Registrazione server di default
load_balancer.register_server('0.0.0.0', 8080)
