import pytest
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.models.models import User, GoldAccount, MoneyAccount
from app.models.noble_system import NobleRank

@pytest.fixture
def transformation_service():
    return TransformationService()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(email='test@example.com')
        money_account = MoneyAccount(balance=Decimal('1000.00'))
        gold_account = GoldAccount(balance=Decimal('0'))
        user.money_account = money_account
        user.gold_account = gold_account
        return user

def test_transform_money_to_gold(app, transformation_service, test_user):
    with app.app_context():
        # Test basic transformation
        euro_amount = Decimal('100.00')
        gold_price = Decimal('50.00')  # price per gram
        
        result = transformation_service.transform(
            test_user,
            euro_amount,
            gold_price
        )
        
        assert result['status'] == 'success'
        assert test_user.money_account.balance == Decimal('900.00')
        assert test_user.gold_account.balance == Decimal('2.00')  # 100/50 = 2 grams

def test_insufficient_funds(app, transformation_service, test_user):
    with app.app_context():
        # Test transformation with insufficient funds
        euro_amount = Decimal('2000.00')  # More than available balance
        gold_price = Decimal('50.00')
        
        with pytest.raises(ValueError, match="Insufficient funds"):
            transformation_service.transform(
                test_user,
                euro_amount,
                gold_price
            )

def test_noble_rank_update(app, transformation_service, test_user):
    with app.app_context():
        # Test if noble rank is updated after significant investment
        euro_amount = Decimal('500.00')
        gold_price = Decimal('50.00')
        
        result = transformation_service.transform(
            test_user,
            euro_amount,
            gold_price
        )
        
        assert result['status'] == 'success'
        assert test_user.noble_rank is not None

@pytest.mark.asyncio
async def test_transformation_validation(app, transformation_service):
    with app.app_context():
        # Test invalid amount
        with pytest.raises(ValueError, match="Amount must be positive"):
            await transformation_service.transform_money_to_gold(
                user_id=1,
                amount=Decimal('-100.00'),
                current_gold_price=Decimal('50.00')
            )
        
        # Test zero amount
        with pytest.raises(ValueError, match="Amount must be positive"):
            await transformation_service.transform_money_to_gold(
                user_id=1,
                amount=Decimal('0.00'),
                current_gold_price=Decimal('50.00')
            )

@pytest.mark.asyncio
async def test_successful_transformation(app, transformation_service, test_user):
    with app.app_context():
        initial_money = test_user.money_account.balance
        initial_gold = test_user.gold_account.balance
        
        amount = Decimal('100.00')
        gold_price = Decimal('50.00')
        
        result = await transformation_service.transform_money_to_gold(
            user_id=test_user.id,
            amount=amount,
            current_gold_price=gold_price
        )
        
        assert result['status'] == 'success'
        assert test_user.money_account.balance == initial_money - amount
        assert test_user.gold_account.balance == initial_gold + (amount / gold_price)

@pytest.mark.asyncio
async def test_transformation_limits(app, transformation_service, test_user):
    with app.app_context():
        # Test daily limit
        daily_limit = Decimal('10000.00')
        amount = daily_limit + Decimal('1.00')
        
        with pytest.raises(ValueError, match="Exceeds daily transformation limit"):
            await transformation_service.transform_money_to_gold(
                user_id=test_user.id,
                amount=amount,
                current_gold_price=Decimal('50.00')
            )
@pytest.mark.asyncio
async def test_validate_transfer(app, transformation_service):
    """Test validazione bonifico da parte del tecnico"""
    with app.app_context():
        # Setup
        technician = User(email='tech@example.com', role='technician')
        client = User(email='client@example.com')
        transaction = Transaction(
            user_id=client.id,
            amount=Decimal('1000.00'),
            status='pending'
        )
        db.session.add_all([technician, client, transaction])
        db.session.commit()

        # Test validazione
        result = await transformation_service.validate_transfer(technician.id, transaction.id)
        assert result['status'] == 'success'
        assert transaction.status == 'validated'
        assert transaction.validated_by == technician.id

@pytest.mark.asyncio
async def test_tuesday_gold_purchase(app, transformation_service):
    """Test acquisto oro del martedì"""
    with app.app_context():
        # Setup
        technician = User(email='tech@example.com', role='technician')
        client = User(email='client@example.com')
        money_account = MoneyAccount(user_id=client.id, balance=Decimal('1000.00'))
        gold_account = GoldAccount(user_id=client.id, balance=Decimal('0'))
        
        db.session.add_all([technician, client, money_account, gold_account])
        db.session.commit()

        # Test acquisto oro
        fixing_price = Decimal('1850.00')
        result = await transformation_service.execute_tuesday_gold_purchase(technician.id, fixing_price)
        
        assert result['status'] == 'success'
        assert result['summary']['total_euro'] == float(Decimal('1000.00'))
        assert money_account.balance == Decimal('0')
        assert gold_account.balance > Decimal('0')
