
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.weekly_processing_service import WeeklyProcessingService
from app.services.transformation_service import TransformationService

@pytest.mark.asyncio
async def test_weekly_processing_empty_accounts(app, db):
    async with app.app_context():
        service = WeeklyProcessingService()
        result = await service.process_weekly_transformations(Decimal('50.00'))
        assert result['status'] == 'success'
        assert result['processed_users'] == 0
        assert result['total_gold_grams'] == 0

@pytest.mark.asyncio
async def test_weekly_processing_with_balance(app, db, setup_accounts):
    async with app.app_context():
        user, money_account, gold_account = setup_accounts
        money_account.balance = Decimal('1000.00')
        db.session.add(user)
        await db.session.commit()
        
        service = WeeklyProcessingService()
        result = await service.process_weekly_transformations(Decimal('50.00'))
        
        assert result['status'] == 'success'
        assert result['processed_users'] == 1
        assert Decimal(str(result['total_gold_grams'])) > Decimal('0')
        assert money_account.balance == Decimal('0.00')

@pytest.mark.asyncio
async def test_weekly_processing_fee_calculation(app, db, setup_accounts):
    async with app.app_context():
        user, money_account, gold_account = setup_accounts
        money_account.balance = Decimal('1000.00')
        db.session.add(user)
        await db.session.commit()
        
        service = WeeklyProcessingService()
        result = await service.process_weekly_transformations(Decimal('50.00'))
        
        expected_gold = (Decimal('1000.00') * Decimal('0.95')) / Decimal('50.00')
        assert Decimal(str(result['total_gold_grams'])) == expected_gold

@pytest.mark.asyncio
async def test_weekly_processing_multiple_users(app, db, setup_test_data):
    async with app.app_context():
        service = WeeklyProcessingService()
        result = await service.process_weekly_transformations(Decimal('50.00'))
        
        assert result['status'] == 'success'
        assert result['processed_users'] == 3
        assert Decimal(str(result['total_gold_grams'])) == Decimal('57.0')  # (3000 * 0.95) / 50
        
        # Verify accounts were updated correctly
        users = await User.query.all()
        for user in users:
            assert user.money_account.balance == Decimal('0.00')
            assert user.gold_account.balance > Decimal('0.00')
@pytest.fixture
async def setup_test_data(app, db):
    async with app.app_context():
        users = []
        for i in range(3):
            user = User(
                username=f"test_user_{i}",
                email=f"test{i}@example.com",
                password_hash="test_hash"
            )
            money_account = MoneyAccount(balance=Decimal('1000.00'))
            gold_account = GoldAccount(balance=Decimal('0.00'))
            user.money_account = money_account
            user.gold_account = gold_account
            users.append(user)
            db.session.add(user)
        
        await db.session.commit()
        return users
@pytest.mark.asyncio
async def test_validate_weekly_transformation_process(app, db):
    async with app.app_context():
        # Setup
        service = WeeklyProcessingService()
        users = []
        initial_balance = Decimal('1000.00')
        gold_price = Decimal('50.00')
        
        # Create test users with accounts
        for i in range(3):
            user = User(
                username=f"test_user_{i}",
                email=f"test{i}@example.com",
                password_hash="test_hash"
            )
            money_account = MoneyAccount(balance=initial_balance)
            gold_account = GoldAccount(balance=Decimal('0.00'))
            user.money_account = money_account
            user.gold_account = gold_account
            users.append(user)
            db.session.add(user)
        
        await db.session.commit()

        # Execute transformation
        result = await service.process_weekly_transformations(gold_price)

        # Validate response structure
        assert result['status'] == 'success'
        assert result['processed_users'] == 3
        assert 'total_gold_grams' in result
        assert 'fixing_price' in result
        assert 'timestamp' in result

        # Validate calculations
        expected_gold = (initial_balance * Decimal('0.95')) / gold_price
        total_gold = Decimal(str(result['total_gold_grams']))
        assert total_gold == expected_gold * 3

        # Validate account states
        for user in users:
            await db.session.refresh(user)
            assert user.money_account.balance == Decimal('0.00')
            assert user.gold_account.balance > Decimal('0.00')
            assert user.gold_account.balance == expected_gold
