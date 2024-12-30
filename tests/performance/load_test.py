
from locust import HttpUser, task, between
import os

# Configure Locust for Replit environment
if os.getenv('REPL_ID'):
    import gevent.monkey
    gevent.monkey.patch_all()

class GoldInvestmentUser(HttpUser):
    wait_time = between(1, 3)  # Random wait between requests
    
    @task(1)
    def get_health(self):
        self.client.get("/api/v1/health")
    
    @task(2)
    def get_transformations(self):
        self.client.get("/api/v1/transformations")
        
    @task(3)
    def post_transformation(self):
        payload = {
            "amount": 100.0,
            "user_id": 1
        }
        self.client.post("/api/v1/transformations", json=payload)
