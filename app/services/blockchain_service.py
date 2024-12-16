
from typing import Dict, List, Any, Callable
import asyncio
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.batch = []
        
    async def add_to_batch(self, user_address: str, euro_amount: Decimal, 
                          gold_grams: Decimal, fixing_price: Decimal) -> bool:
        try:
            self.batch.append({
                'user_address': user_address,
                'euro_amount': euro_amount,
                'gold_grams': gold_grams,
                'fixing_price': fixing_price
            })
            return True
        except Exception as e:
            logger.error(f"Error adding to batch: {e}")
            return False

    async def process_batch(self) -> Dict[str, Any]:
        if not self.batch:
            return {'status': 'error', 'message': 'Empty batch'}
            
        try:
            # Process the batch here
            transaction_hash = '0x123...abc'  # Placeholder
            self.batch = []  # Clear batch after processing
            return {
                'status': 'success',
                'transaction_hash': transaction_hash
            }
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            return {'status': 'error', 'message': str(e)}

    async def get_user_transactions(self, address: str) -> List[Dict]:
        try:
            # Mock implementation
            return [{
                'timestamp': 1639497600,
                'euro_amount': 1000.00,
                'gold_grams': 0.5,
                'fixing_price': 1800.50
            }]
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []

    async def retry_operation(self, operation: Callable, max_retries: int = 3, delay: float = 1.0) -> Dict[str, Any]:
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(delay)
