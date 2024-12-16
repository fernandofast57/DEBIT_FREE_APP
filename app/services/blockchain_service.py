
from typing import Dict, List
from decimal import Decimal
from web3 import Web3
import logging
import asyncio

# Configurazione del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.batch = []
        self.w3 = Web3()

    async def add_to_batch(self, user_address: str, euro_amount: Decimal, 
                          gold_grams: Decimal, fixing_price: Decimal) -> bool:
        try:
            logger.info("Adding transaction to batch for user: %s", user_address)
            self.batch.append({
                'address': user_address,
                'euro_amount': euro_amount,
                'gold_grams': gold_grams,
                'fixing_price': fixing_price
            })
            return True
        except Exception as e:
            logger.error("Failed to add transaction to batch: %s", str(e))
            return False

    async def process_batch(self) -> Dict:
        try:
            if not self.batch:
                logger.warning("Batch is empty, nothing to process")
                return {
                    'status': 'error',
                    'message': 'Batch is empty'
                }

            logger.info("Processing batch with %d transactions", len(self.batch))
            # Simulazione transazione blockchain
            await asyncio.sleep(1)  # Simula ritardo di rete

            # Reset batch dopo la simulazione
            self.batch = []
            return {
                'status': 'success',
                'transaction_hash': '0x123...abc'
            }
        except Exception as e:
            logger.error("Error processing batch: %s", str(e))
            return {
                'status': 'error',
                'message': str(e)
            }

    async def get_user_transactions(self, address: str) -> List[Dict]:
        try:
            logger.info("Fetching transactions for user address: %s", address)
            # Simulazione recupero transazioni
            await asyncio.sleep(0.5)  # Simula ritardo di rete
            return [{
                'timestamp': 1639497600,
                'euro_amount': 1000.00,
                'gold_grams': 0.5,
                'fixing_price': 1800.50
            }]
        except Exception as e:
            logger.error("Failed to fetch user transactions: %s", str(e))
            return []

    async def retry_operation(self, operation, retries: int = 3, delay: float = 2.0):
        try:
            for attempt in range(retries):
                try:
                    return await operation()
                except Exception as e:
                    logger.warning(
                        "Retry %d/%d failed: %s", attempt + 1, retries, str(e)
                    )
                    if attempt < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        raise
        except Exception as e:
            logger.error("Operation failed after %d retries", retries)
            raise
