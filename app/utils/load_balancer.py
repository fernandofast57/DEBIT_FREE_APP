
import random
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis
from app.utils.cache.redis_manager import cache_manager

logger = logging.getLogger(__name__)

class LoadBalancer:
    def __init__(self):
        self.servers: List[Dict] = []
        self.redis = cache_manager.redis
        self.health_check_interval = 30
        self.metrics_key = "load_balancer:metrics"
        
    async def register_server(self, host: str, port: int, weight: int = 1):
        server = {
            'host': host,
            'port': port,
            'weight': weight,
            'healthy': True,
            'load': 0,
            'last_check': datetime.now(),
            'response_times': []
        }
        self.servers.append(server)
        await self.redis.hset(
            f"server:{host}:{port}",
            mapping={"health": "1", "load": "0"}
        )
        logger.info(f"Registered new server {host}:{port} with weight {weight}")

    async def health_check(self, server: Dict) -> bool:
        try:
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                url = f"http://{server['host']}:{server['port']}/health"
                async with session.get(url, timeout=2) as response:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    server['response_times'].append(elapsed)
                    if len(server['response_times']) > 10:
                        server['response_times'].pop(0)
                    return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed for {server['host']}:{server['port']}: {e}")
            return False

    async def update_health_status(self):
        while True:
            for server in self.servers:
                healthy = await self.health_check(server)
                server['healthy'] = healthy
                server['last_check'] = datetime.now()
                await self.redis.hset(
                    f"server:{server['host']}:{server['port']}",
                    "health", "1" if healthy else "0"
                )
            await asyncio.sleep(self.health_check_interval)

    async def get_next_server(self) -> Optional[Dict]:
        healthy_servers = [s for s in self.servers if s['healthy']]
        if not healthy_servers:
            logger.error("No healthy servers available")
            return None
            
        # Weighted round-robin con considerazione del carico
        candidates = []
        min_load_per_weight = float('inf')
        
        for server in healthy_servers:
            load_per_weight = server['load'] / server['weight']
            if load_per_weight < min_load_per_weight:
                min_load_per_weight = load_per_weight
                candidates = [server]
            elif load_per_weight == min_load_per_weight:
                candidates.append(server)
        
        # Scegli il server con il minor tempo di risposta medio
        selected = min(candidates, 
                      key=lambda s: sum(s['response_times'])/len(s['response_times']) 
                      if s['response_times'] else float('inf'))
        
        selected['load'] += 1
        await self.redis.hincrby(
            f"server:{selected['host']}:{selected['port']}", 
            "load", 
            1
        )
        
        return selected

    async def release_server(self, server: Dict):
        if server and server in self.servers:
            server['load'] = max(0, server['load'] - 1)
            await self.redis.hincrby(
                f"server:{server['host']}:{server['port']}", 
                "load", 
                -1
            )

    async def get_metrics(self) -> Dict:
        metrics = {
            'total_servers': len(self.servers),
            'healthy_servers': len([s for s in self.servers if s['healthy']]),
            'total_load': sum(s['load'] for s in self.servers),
            'average_response_time': {}
        }
        
        for server in self.servers:
            if server['response_times']:
                avg_time = sum(server['response_times']) / len(server['response_times'])
                metrics['average_response_time'][f"{server['host']}:{server['port']}"] = avg_time
                
        await self.redis.hset(self.metrics_key, mapping=metrics)
        return metrics

load_balancer = LoadBalancer()

async def init_load_balancer():
    await load_balancer.register_server('0.0.0.0', 8080, weight=2)

# Initialize the event loop and run the registration
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(init_load_balancer())
