
from typing import Dict, Any, Optional, List
from decimal import Decimal
import asyncio
from web3.exceptions import ContractLogicError
from app.utils.logging_config import get_logger
from app.models.noble_system import NobleRank
from app.services.blockchain_service import BlockchainService
from app.utils.retry import retry_with_backoff

logger = get_logger(__name__)

class BlockchainNobleService:
    def __init__(self, blockchain_service: Optional[BlockchainService] = None):
        self.blockchain_service = blockchain_service or BlockchainService()
        self._cache = {}
        
    async def update_noble_rank(self, user_address: str, rank_id: int) -> Dict[str, Any]:
        """Aggiorna il rank nobile sulla blockchain"""
        if not self.blockchain_service.is_connected():
            logger.error("Blockchain service not connected")
            return {'status': 'error', 'message': 'Blockchain service not connected'}
            
        try:
            noble_rank = await NobleRank.get_by_id(rank_id)
            if not noble_rank:
                return {'status': 'error', 'message': 'Invalid rank ID'}
                
            transaction = await self.blockchain_service.update_noble_rank(
                address=user_address,
                rank=rank_id
            )
            
            if transaction['status'] == 'verified':
                await self._update_cache(user_address, rank_id)
                return {
                    'status': 'success',
                    'transaction_hash': transaction['transaction_hash'],
                    'rank': noble_rank.name
                }
            
            return {'status': 'error', 'message': 'Transaction failed'}
            
        except ContractLogicError as e:
            logger.error(f"Contract error in update_noble_rank: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            logger.error(f"Error in update_noble_rank: {str(e)}")
            return {'status': 'error', 'message': 'Internal service error'}

    @retry_with_backoff(max_retries=3)
    async def get_noble_rank(self, address: str) -> Dict[str, Any]:
        """Recupera il rank nobile corrente dalla blockchain"""
        try:
            if cached_rank := self._cache.get(address):
                return cached_rank
                
            contract = self.blockchain_service.contract
            rank_id = await contract.functions.getRank(address).call()
            noble_rank = await NobleRank.get_by_id(rank_id)
            
            if not noble_rank:
                return {'status': 'error', 'message': 'Invalid rank ID'}
                
            result = {
                'status': 'success',
                'rank_id': rank_id,
                'rank_name': noble_rank.name,
                'benefits': noble_rank.benefits
            }
            
            await self._update_cache(address, rank_id)
            return result
            
        except Exception as e:
            logger.error(f"Error getting noble rank: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def _update_cache(self, address: str, rank_id: int) -> None:
        """Aggiorna la cache interna dei rank"""
        try:
            noble_rank = await NobleRank.get_by_id(rank_id)
            if noble_rank:
                self._cache[address] = {
                    'status': 'success',
                    'rank_id': rank_id,
                    'rank_name': noble_rank.name,
                    'benefits': noble_rank.benefits
                }
        except Exception as e:
            logger.error(f"Cache update error: {str(e)}")

    async def verify_noble_benefits(self, address: str) -> Dict[str, Any]:
        """Verifica i benefit del rank nobile"""
        try:
            rank_info = await self.get_noble_rank(address)
            if rank_info['status'] != 'success':
                return rank_info
                
            benefits = rank_info.get('benefits', {})
            return {
                'status': 'success',
                'address': address,
                'rank_name': rank_info['rank_name'],
                'active_benefits': benefits,
                'verification_time': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Benefit verification error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def get_noble_statistics(self) -> Dict[str, Any]:
        """Recupera statistiche del sistema noble"""
        try:
            contract = self.blockchain_service.contract
            total_nobles = await contract.functions.getTotalNobles().call()
            stats = {
                'status': 'success',
                'total_nobles': total_nobles,
                'ranks_distribution': await self._get_ranks_distribution(),
                'cache_size': len(self._cache)
            }
            return stats
            
        except Exception as e:
            logger.error(f"Error getting noble statistics: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def _get_ranks_distribution(self) -> Dict[str, int]:
        """Calcola la distribuzione dei rank"""
        try:
            ranks = await NobleRank.get_all()
            distribution = {}
            contract = self.blockchain_service.contract
            
            for rank in ranks:
                count = await contract.functions.getRankCount(rank.id).call()
                distribution[rank.name] = count
                
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating rank distribution: {str(e)}")
            return {}
