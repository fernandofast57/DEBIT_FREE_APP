
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.bonus_distribution_service import BonusDistributionService
from app.models.noble_system import NobleRank, NobleRelation, BonusTransaction

@pytest.fixture
def bonus_service():
    return BonusDistributionService()

@pytest.fixture
def noble_user(app):
    with app.app_context():
        user = User(email='noble@test.com', noble_rank='noble')
        money_account = MoneyAccount(balance=Decimal('0.00'))
        gold_account = GoldAccount(balance=Decimal('10.00'))
        user.money_account = money_account
        user.gold_account = gold_account
        return user

@pytest.fixture
def referral_users(app):
    with app.app_context():
        users = []
        for i in range(3):
            user = User(email=f'referral{i}@test.com', noble_rank='noble')
            money_account = MoneyAccount(balance=Decimal('1000.00'))
            gold_account = GoldAccount(balance=Decimal('0.00'))
            user.money_account = money_account
            user.gold_account = gold_account
            users.append(user)
        return users

def test_bonus_calculation(app, bonus_service, noble_user, referral_users):
    with app.app_context():
        # Setup referral network
        for referral in referral_users:
            relation = NobleRelation(
                referrer=noble_user,
                referred=referral,
                rank=NobleRank.query.filter_by(title='noble').first()
            )
            db.session.add(relation)
        
        transaction_amount = Decimal('1000.00')
        bonus = bonus_service.calculate_bonus(noble_user, transaction_amount)
        
        assert bonus > 0
        assert isinstance(bonus, Decimal)

def test_bonus_distribution(app, bonus_service, noble_user, referral_users):
    with app.app_context():
        initial_balance = noble_user.money_account.balance
        transaction_amount = Decimal('1000.00')
        
        bonus_service.distribute_bonus(
            user=noble_user,
            transaction_amount=transaction_amount
        )
        
        # Verify bonus transaction was recorded
        bonus_tx = BonusTransaction.query.filter_by(user_id=noble_user.id).first()
        assert bonus_tx is not None
        assert bonus_tx.transaction_amount == transaction_amount
        
        # Verify money account was updated
        assert noble_user.money_account.balance > initial_balance

def test_rank_based_bonus(app, bonus_service, noble_user):
    with app.app_context():
        # Test bonus rates for different ranks
        ranks = ['noble', 'viscount', 'count']
        amounts = []
        
        transaction_amount = Decimal('1000.00')
        
        for rank in ranks:
            noble_user.noble_rank = rank
            bonus = bonus_service.calculate_bonus(noble_user, transaction_amount)
            amounts.append(bonus)
        
        # Higher ranks should get higher bonuses
        assert amounts[0] < amounts[1] < amounts[2]
import pytest
from decimal import Decimal
from app.services.bonus_distribution_service import BonusDistributionService

@pytest.mark.asyncio
async def test_multi_level_bonus_distribution(app, bonus_service):
    """Test bonus distribution across multiple levels matches the specification"""
    async with app.app_context():
        # Setup users A -> A' -> A'' -> A'''
        user_a = User(email='a@test.com')
        user_a1 = User(email='a1@test.com', referrer_id=user_a.id)
        user_a2 = User(email='a2@test.com', referrer_id=user_a1.id)
        user_a3 = User(email='a3@test.com', referrer_id=user_a2.id)
        
        db.session.add_all([user_a, user_a1, user_a2, user_a3])
        await db.session.commit()

        # Test A''' makes purchase
        purchase_amount = Decimal('1000.00')
        result = await bonus_service.distribute_affiliate_bonus(user_a3.id, purchase_amount)
        
        # Verify A'' gets 0.7%
        assert result[user_a2.id]['bonus'] == float(purchase_amount * Decimal('0.007'))
        # Verify A' gets 0.5%  
        assert result[user_a1.id]['bonus'] == float(purchase_amount * Decimal('0.005'))
        # Verify A gets 0.5%
        assert result[user_a.id]['bonus'] == float(purchase_amount * Decimal('0.005'))

        # Verify total bonus is 1.7%
        total_bonus = sum(r['bonus'] for r in result.values())
        assert abs(total_bonus - float(purchase_amount * Decimal('0.017'))) < 0.0001
