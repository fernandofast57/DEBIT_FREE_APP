
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
async def test_weekly_processing_multiple_users(app, db):
    async with app.app_context():
        service = WeeklyProcessingService()
        users = []
        
        try:
            for i in range(3):
                user = User(username=f"test_user_{i}", email=f"test{i}@example.com")
                money_account = MoneyAccount(balance=Decimal('1000.00'))
                gold_account = GoldAccount(balance=Decimal('0.00'))
                user.money_account = money_account
                user.gold_account = gold_account
                users.append(user)
                db.session.add(user)
            
            await db.session.commit()
        result = await service.process_weekly_transformations(Decimal('50.00'))
        assert result['processed_users'] == 3
        assert Decimal(str(result['total_gold_grams'])) == Decimal('57.0')  # (3000 * 0.95) / 50
