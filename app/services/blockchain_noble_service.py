
from web3 import Web3
from decimal import Decimal
from app.models.noble_system import NobleRank, BonusTransaction
from app.utils.logging_config import logger

class BlockchainNobleService:
    def __init__(self, web3_provider, contract_address):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=self.load_contract_abi()
        )
        
    async def update_noble_rank(self, user_address: str, new_rank: str) -> dict:
        try:
            tx_hash = await self.contract.functions.updateNobleRank(
                user_address,
                new_rank
            ).transact()
            
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                'status': 'success',
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'rank': new_rank
            }
        except Exception as e:
            logger.error(f"Error updating noble rank: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def distribute_noble_bonus(self, user_address: str, amount: Decimal) -> dict:
        try:
            tx_hash = await self.contract.functions.distributeNobleBonus(
                user_address,
                int(amount * 10**18)
            ).transact()
            
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                'status': 'success',
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber
            }
        except Exception as e:
            logger.error(f"Error distributing noble bonus: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def update_noble_rank(self, user_address: str, new_rank: str) -> dict:
        try:
            tx_hash = await self.contract.functions.updateNobleRank(
                user_address,
                new_rank
            ).transact()
            
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                'status': 'success',
                'tx_hash': receipt.transactionHash.hex()
            }
        except Exception as e:
            logger.error(f"Error updating noble rank: {str(e)}")
            return {'status': 'error', 'message': str(e)}
