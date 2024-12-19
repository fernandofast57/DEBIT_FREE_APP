
from decimal import Decimal
from typing import Optional
from app.models.models import User, NobleRank
from app.services.blockchain_noble_service import BlockchainNobleService
from app.utils.logging_config import logger

class NobleRankService:
    def __init__(self):
        self.rank_requirements = {
            'Knight': Decimal('10000'),    # 10,000 EUR
            'Baron': Decimal('50000'),     # 50,000 EUR
            'Count': Decimal('100000'),    # 100,000 EUR
            'Duke': Decimal('500000')      # 500,000 EUR
        }
        
    async def calculate_new_rank(self, user: User) -> Optional[str]:
        """Calculate new rank based on investment volume"""
        total_investment = user.total_investment
        
        for rank, requirement in sorted(self.rank_requirements.items(), 
                                     key=lambda x: x[1], reverse=True):
            if total_investment >= requirement:
                return rank
                
        return 'Knight'  # Default rank
        
    async def update_user_rank(self, user: User) -> bool:
        try:
            new_rank = await self.calculate_new_rank(user)
            if new_rank != user.noble_rank.rank_name:
                blockchain_service = BlockchainNobleService(
                    web3_provider=os.getenv('RPC_ENDPOINTS').split(',')[0],
                    contract_address=os.getenv('CONTRACT_ADDRESS')
                )
                
                result = await blockchain_service.update_noble_rank(
                    user.blockchain_address, 
                    new_rank
                )
                
                if result['status'] == 'success':
                    user.noble_rank.rank_name = new_rank
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error updating noble rank: {str(e)}")
            return False
