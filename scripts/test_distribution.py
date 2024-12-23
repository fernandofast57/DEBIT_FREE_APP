
from app import create_app, db
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.weekly_processing_service import WeeklyProcessingService
from decimal import Decimal

def run_distribution_test():
    app = create_app()
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hash123'
        )
        money_account = MoneyAccount(balance=1000.0)
        gold_account = GoldAccount(balance=0.0)
        
        user.money_account = money_account
        user.gold_account = gold_account
        
        db.session.add(user)
        db.session.commit()
        
        # Run distribution process
        service = WeeklyProcessingService()
        service.process_weekly_transactions(fixing_price=Decimal('50.0'))
        
        # Print results
        print(f"Money Account Balance: {user.money_account.balance}")
        print(f"Gold Account Balance: {user.gold_account.balance}")

if __name__ == '__main__':
    run_distribution_test()
