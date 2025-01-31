
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import logging
from web3 import Web3
from app.models.noble_system import NobleRank
from app.utils.logging_config import get_logger
from app.services.blockchain_service import BlockchainService
from app.utils.monitoring.blockchain_monitor import BlockchainMonitor

logger = get_logger(__name__)

class ServizioNobileBlockchain:
    """Service for handling noble-related blockchain operations"""
    
    def __init__(self, blockchain_service: Optional[BlockchainService] = None):
        self.blockchain_service = blockchain_service or BlockchainService()
        self.monitor = BlockchainMonitor(self.blockchain_service.w3)
        self.logger = logging.getLogger(__name__)

    async def update_noble_rank(self, 
                              address: str, 
                              rank_id: int,
                              user_id: int) -> Dict[str, Any]:
        """
        Update noble rank on blockchain
        
        Args:
            address: User's blockchain address
            rank_id: New noble rank ID
            user_id: User's ID in the system
        """
        try:
            if not self.blockchain_service.w3.is_address(address):
                return {
                    'status': 'error',
                    'message': 'Invalid blockchain address'
                }

            noble_rank = await NobleRank.get_by_id(rank_id)
            if not noble_rank:
                return {
                    'status': 'error',
                    'message': 'Invalid noble rank ID'
                }

            result = await self.blockchain_service.send_transaction(
                self.blockchain_service.contract.functions.updateNobleRank(
                    address,
                    rank_id
                )
            )

            await self.monitor.monitor_transactions({
                'type': 'noble_rank_update',
                'user_id': user_id,
                'rank_id': rank_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': result['status'],
                'tx_hash': result.get('transaction_hash')
            })

            return result

        except Exception as e:
            self.logger.error(f"Error updating noble rank: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def verify_noble_status(self, 
                                address: str,
                                min_rank: int) -> Dict[str, bool]:
        """
        Verify if address has required noble rank
        
        Args:
            address: Blockchain address to check
            min_rank: Minimum required rank
        """
        try:
            if not self.blockchain_service.w3.is_address(address):
                return {'is_valid': False}

            current_rank = await self.blockchain_service.contract.functions.nobleRanks(
                address
            ).call()

            return {
                'is_valid': current_rank >= min_rank,
                'current_rank': current_rank
            }

        except Exception as e:
            self.logger.error(f"Error verifying noble status: {str(e)}")
            return {'is_valid': False}

    async def calculate_noble_bonus(self,
                                  address: str,
                                  amount: Decimal) -> Dict[str, Any]:
        """
        Calculate bonus based on noble rank
        
        Args:
            address: User's blockchain address
            amount: Base amount for bonus calculation
        """
        try:
            status = await self.verify_noble_status(address, 1)
            if not status['is_valid']:
                return {'bonus_amount': Decimal('0')}

            premio_referral = {
                1: Decimal('0.007'),  # Livello 1: 0.7% del peso
                2: Decimal('0.005'),  # Livello 2: 0.5% del peso
                3: Decimal('0.005')   # Livello 3: 0.5% del peso
            }

            multiplier = premio_referral.get(
                status['current_level'],
                Decimal('0')
            )
            bonus_amount = (amount * multiplier).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

            return {
                'status': 'success',
                'bonus_amount': bonus_amount,
                'rank': status['current_rank']
            }

        except Exception as e:
            self.logger.error(f"Error calculating noble bonus: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def get_noble_stats(self, address: str) -> Dict[str, Any]:
        """Get noble system statistics for address"""
        try:
            if not self.blockchain_service.w3.is_address(address):
                return {'status': 'error', 'message': 'Invalid address'}

            current_rank = await self.blockchain_service.contract.functions.nobleRanks(
                address
            ).call()

            total_rewards = await self.blockchain_service.contract.functions.totalRewards(
                address
            ).call()

            return {
                'status': 'success',
                'current_rank': current_rank,
                'total_rewards': self.blockchain_service.w3.from_wei(total_rewards, 'ether'),
                'address': address
            }

        except Exception as e:
            self.logger.error(f"Error getting noble stats: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
