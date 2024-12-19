
import pytest
from decimal import Decimal
from app.services.bonus_distribution_service import BonusDistributionService
from app.models.models import User, NobleRank
from app.models.noble_system import NobleRelation

@pytest.fixture
def bonus_service():
    return BonusDistributionService()

def test_calculate_bonus(bonus_service, app):
    with app.app_context():
        user = User(id=1, email='test@test.com')
        rank = NobleRank(title='Duke', bonus_rate=Decimal('0.05'))
        user.noble_rank = rank
        user.gold_account.balance = Decimal('1000')
        
        bonus = bonus_service.calculate_user_bonus(user)
        assert bonus == Decimal('50')  # 5% of 1000

def test_bonus_distribution(bonus_service, app):
    with app.app_context():
        results = bonus_service.distribute_monthly_bonus()
        assert isinstance(results, dict)
