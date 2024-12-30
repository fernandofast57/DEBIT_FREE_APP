
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.services.transformation_service import TransformationService
from tests.helpers import get_test_auth_headers

@pytest.mark.parametrize("euro_amount,fixing_price,fee_amount,gold_grams", [
    (150.00, 50.00, 5.00, 3.5),
    (1000.00, 55.00, 10.00, 18.18),
    (500.00, 52.50, 7.50, 9.52)
])
def test_valid_transformation(app, client, euro_amount, fixing_price, fee_amount, gold_grams):
    """Test valid transformation request with database verification"""
    with app.app_context():
        # Create test user with accounts if not exists
        user = User.query.first()
        if not user:
            user = User(username="testuser", email="test@example.com")
            user.money_account = MoneyAccount(balance=Decimal('2000.00'))
            user.gold_account = GoldAccount(balance=Decimal('0.00'))
            app.db.session.add(user)
            app.db.session.commit()

        assert user.money_account is not None, "User lacks a MoneyAccount"
        assert user.gold_account is not None, "User lacks a GoldAccount"
        
        # Ensure sufficient balance
        if user.money_account.balance < Decimal(str(euro_amount)):
            user.money_account.balance = Decimal(str(euro_amount)) * Decimal('2')
            app.db.session.commit()
        
        # Get initial balances
        initial_gold_balance = user.gold_account.balance
        initial_money_balance = user.money_account.balance
        
        # Perform transformation
        headers = get_test_auth_headers()
        response = client.post('/api/v1/transformations/transform', headers=headers, json={
            "euro_amount": euro_amount,
            "fixing_price": fixing_price,
            "fee_amount": fee_amount,
            "gold_grams": gold_grams
        })
        
        assert response.status_code == 200, f"Failed with status {response.status_code}: {response.get_json()}"
        
        # Refresh user data
        app.db.session.refresh(user)
        
        # Verify balances
        assert user.gold_account.balance == initial_gold_balance + Decimal(str(gold_grams))
        assert user.money_account.balance == initial_money_balance - Decimal(str(euro_amount))
        
        # Verify transformation record
        transformation = GoldTransformation.query.filter_by(user_id=user.id).order_by(GoldTransformation.created_at.desc()).first()
        assert transformation is not None
        assert transformation.euro_amount == Decimal(str(euro_amount))
        assert transformation.gold_grams == Decimal(str(gold_grams))
