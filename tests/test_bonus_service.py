import pytest
import asyncio
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.services.bonus_distribution_service import BonusDistributionService
from app.models.models import User, GoldReward, GoldAccount, db
from app.utils.errors import InvalidRankError, InsufficientBalanceError

@pytest.mark.asyncio
class TestBonusDistributionService:
    
    @pytest.fixture
    async def setup_test_data(self):
        test_user = User(id=1, username="Test User", email="test@example.com", referrer_id=None)
        gold_account = GoldAccount(user_id=1, balance=Decimal('10.0000'))
        test_user.gold_account = gold_account
        db.session.add(test_user)
        db.session.add(gold_account)
        await db.session.commit()
        return test_user

    @pytest.fixture
    def bonus_service(self):
        return BonusDistributionService()

    @pytest.mark.asyncio
    async def test_distribute_structure_bonus(self, bonus_service, setup_test_data):
        user = setup_test_data
        euro_amount = Decimal('100.00')
        fixing_price = Decimal('50.0000')
        
        result = await bonus_service.distribute_structure_bonus(
            user_id=user.id, 
            euro_amount=euro_amount, 
            fixing_price=fixing_price
        )
        
        assert isinstance(result, dict)
        assert len(result) == 0
        
        operational_bonus = await GoldReward.query.filter_by(reward_type='operational').one_or_none()
        assert operational_bonus is not None
        assert operational_bonus.gold_amount > 0

    @pytest.mark.asyncio
    async def test_distribute_rewards_successful(self, bonus_service, setup_test_data):
        euro_amount = Decimal('1000.00')
        fixing_price = Decimal('50.0000')
        
        result = await bonus_service.distribute_rewards(
            user_id=setup_test_data.id,
            euro_amount=euro_amount,
            fixing_price=fixing_price
        )
        
        assert 'structure_rewards' in result
        assert 'achievement_reward' in result
        assert 'timestamp' in result
        
        assert isinstance(result['structure_rewards'], dict)
        assert isinstance(result['achievement_reward'], dict) or result['achievement_reward'] is None