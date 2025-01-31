
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from app.services.bonus_distribution_service import BonusDistributionService
from app.models import User, NobleRelation, GoldAccount, db

@pytest.fixture
def mock_db_session():
    session = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    return session

@pytest.fixture
def bonus_service(mock_db_session):
    with patch('app.services.bonus_distribution_service.db.session', mock_db_session):
        service = BonusDistributionService()
        return service

@pytest.mark.asyncio
async def test_calculate_purchase_bonuses(bonus_service):
    # Setup test data
    purchase_amount = Decimal('1000.00')
    user_id = 1
    
    mock_user = Mock(id=user_id, referrer_id=2)
    mock_referrer = Mock(id=2, referrer_id=3)
    
    with patch.object(bonus_service, '_get_bonus_rate') as mock_rate:
        mock_rate.return_value = Decimal('0.007')
        
        bonuses = await bonus_service.calculate_purchase_bonuses(user_id, purchase_amount)
        
        assert len(bonuses) > 0
        assert all(bonus['rate'] > 0 for bonus in bonuses.values())

@pytest.mark.asyncio
async def test_distribute_bonuses(bonus_service):
    bonuses = {
        1: {'amount': Decimal('7.00'), 'level': 1, 'rate': Decimal('0.007'), 'type': 'upline'},
        2: {'amount': Decimal('5.00'), 'level': 2, 'rate': Decimal('0.005'), 'type': 'upline'}
    }
    
    result = await bonus_service.distribute_bonuses(bonuses)
    assert result == True

@pytest.mark.asyncio
async def test_invalid_bonus_distribution(bonus_service):
    bonuses = {
        1: {'amount': Decimal('-1.00'), 'level': 1, 'rate': Decimal('0.007'), 'type': 'upline'}
    }
    
    result = await bonus_service.distribute_bonuses(bonuses)
    assert result == False
