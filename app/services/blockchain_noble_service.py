
from web3 import Web3
from decimal import Decimal
from typing import Dict, Any
from app.models.noble_system import NobleRank, BonusTransaction
from app.utils.logging_config import logger

class BlockchainNobleService:
    def __init__(self, web3_provider: str, contract_address: str):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=self.load_contract_abi()
        )
        
    async def update_noble_rank(self, user_address: str, new_rank: str) -> Dict[str, Any]:
        """Update noble rank on blockchain with improved error handling"""
        try:
            if not self.web3.is_address(user_address):
                raise ValueError("Invalid blockchain address")
                
            tx_hash = await self.contract.functions.updateNobleRank(
                user_address,
                new_rank
            ).transact()
            
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if not receipt.status:
                raise Exception("Transaction failed")
                
            return {
                'status': 'success',
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'rank': new_rank
            }
        except Exception as e:
            logger.error(f"Error updating noble rank: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def distribute_noble_bonus(self, user_address: str, amount: Decimal) -> Dict[str, Any]:
        """Distribute noble bonus with validation"""
        try:
            if not self.web3.is_address(user_address):
                raise ValueError("Invalid blockchain address")
                
            if amount <= 0:
                raise ValueError("Invalid bonus amount")
                
            tx_hash = await self.contract.functions.distributeNobleBonus(
                user_address,
                int(amount * 10**18)  # Convert to wei
            ).transact()
            
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if not receipt.status:
                raise Exception("Bonus distribution failed")
                
            return {
                'status': 'success',
                'tx_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'amount': float(amount)
            }
        except Exception as e:
            logger.error(f"Error distributing noble bonus: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def validate_noble_rank(self, user_id: int, rank_id: int) -> bool:
        """Validate noble rank with error handling"""
        try:
            if user_id <= 0 or rank_id <= 0:
                return False
                
            contract = await self._get_contract()
            return await contract.functions.validateNobleRank(user_id, rank_id).call()
        except Exception as e:
            logger.error(f"Noble rank validation failed: {str(e)}")
            return False

    async def _get_contract(self):
        """Get contract instance with validation"""
        if not self.contract:
            raise ValueError("Contract not initialized")
        return self.contract

    def load_contract_abi(self) -> dict:
        """Load contract ABI from configuration"""
        try:
            # Implement ABI loading logic here
            return {}
        except Exception as e:
            logger.error(f"Error loading contract ABI: {str(e)}")
            raise
