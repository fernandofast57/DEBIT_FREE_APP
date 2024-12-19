
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
