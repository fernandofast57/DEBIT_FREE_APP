
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from tests.helpers import get_test_auth_headers
import concurrent.futures

@pytest.fixture
def test_user(app):
    """Create a test user with required accounts"""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.money_account = MoneyAccount(balance=Decimal('2000.00'))
        user.gold_account = GoldAccount(balance=Decimal('0.00'))
        app.db.session.add(user)
        app.db.session.commit()
        return user

def test_valid_transformation(app, client, test_user):
    """Test valid transformation request with database verification"""
    with app.app_context():
        assert test_user is not None, "No test user found"
        assert test_user.money_account is not None, "User lacks a MoneyAccount"
        assert test_user.gold_account is not None, "User lacks a GoldAccount"
        
        headers = get_test_auth_headers(test_user)
        initial_gold_balance = test_user.gold_account.balance
        initial_money_balance = test_user.money_account.balance
        
        response = client.post('/api/v1/transformations/transform', headers=headers, json={
            "euro_amount": 150.00,
            "fixing_price": 50.00,
            "fee_amount": 5.00,
            "gold_grams": 3.5
        })
        
        assert response.status_code == 200, f"Failed with status {response.status_code}: {response.get_json()}"
        assert "Gold transformed successfully" in response.get_json()["message"]
        
        app.db.session.refresh(test_user)
        assert test_user.gold_account.balance == initial_gold_balance + Decimal('3.5')
        assert test_user.money_account.balance == initial_money_balance - Decimal('150.00')
        
        transformation = GoldTransformation.query.filter_by(user_id=test_user.id).order_by(GoldTransformation.created_at.desc()).first()
        assert transformation is not None
        assert transformation.euro_amount == Decimal('150.00')
        assert transformation.gold_grams == Decimal('3.5')

def test_concurrent_transformations(app, client, test_user):
    """Test concurrent transformation requests"""
    with app.app_context():
        headers = get_test_auth_headers(test_user)
        initial_balance = test_user.money_account.balance
        
        def make_request():
            return client.post('/api/v1/transformations/transform', headers=headers, json={
                "euro_amount": 150.00,
                "fixing_price": 50.00,
                "fee_amount": 5.00,
                "gold_grams": 3.5
            })
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [f.result() for f in futures]
        
        successful = sum(1 for r in responses if r.status_code == 200)
        assert successful == 1, "Only one concurrent transformation should succeed"
        
        app.db.session.refresh(test_user)
        expected_balance = initial_balance - Decimal('150.00')
        assert test_user.money_account.balance == expected_balance, "Balance should reflect only one successful transformation"

def test_missing_required_fields(app, client, test_user):
    """Test missing required fields validation"""
    with app.app_context():
        headers = get_test_auth_headers(test_user)
        response = client.post('/api/v1/transformations/transform', headers=headers, json={
            "euro_amount": 150.00
        })
        assert response.status_code == 400
        error_response = response.get_json()["errors"]
        assert all(field in error_response for field in ["fixing_price", "fee_amount", "gold_grams"])

def test_empty_payload(app, client, test_user):
    """Test empty payload validation"""
    with app.app_context():
        headers = get_test_auth_headers(test_user)
        response = client.post('/api/v1/transformations/transform', headers=headers, json={})
        assert response.status_code == 400
        error_response = response.get_json()["errors"]
        assert all(field in error_response for field in ["euro_amount", "fixing_price", "fee_amount", "gold_grams"])
