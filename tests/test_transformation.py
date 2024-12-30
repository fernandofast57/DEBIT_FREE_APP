
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
        with client:
            headers = get_test_auth_headers()
            
            # Get initial balances
            user = User.query.first()
            initial_gold_balance = user.gold_account.balance
            initial_money_balance = user.money_account.balance
            
            response = client.post('/api/v1/transformations/transform', headers=headers, json={
                "euro_amount": euro_amount,
                "fixing_price": fixing_price,
                "fee_amount": fee_amount,
                "gold_grams": gold_grams
            })
            
            assert response.status_code == 200
            assert "Gold transformed successfully" in response.get_json()["message"]
            
            # Verify database updates
            user = User.query.first()
            assert user.gold_account.balance == initial_gold_balance + Decimal(str(gold_grams))
            assert user.money_account.balance == initial_money_balance - Decimal(str(euro_amount))
            
            # Verify transformation record
            transformation = GoldTransformation.query.filter_by(user_id=user.id).order_by(GoldTransformation.created_at.desc()).first()
            assert transformation is not None
            assert transformation.euro_amount == Decimal(str(euro_amount))
            assert transformation.gold_grams == Decimal(str(gold_grams))

def test_concurrent_transformations(app, client):
    """Test concurrent transformation requests"""
    with app.app_context():
        with client:
            headers = get_test_auth_headers()
            import concurrent.futures
            
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

def test_missing_required_fields(app, client):
    """Test missing required fields validation"""
    with app.app_context():
        with client:
            headers = get_test_auth_headers()
            response = client.post('/api/v1/transformations/transform', headers=headers, json={
                "euro_amount": 150.00
            })
            assert response.status_code == 400
            error_response = response.get_json()["errors"]
            assert all(field in error_response for field in ["fixing_price", "fee_amount", "gold_grams"])

def test_empty_payload(app, client):
    """Test empty payload validation"""
    with app.app_context():
        with client:
            headers = get_test_auth_headers()
            response = client.post('/api/v1/transformations/transform', headers=headers, json={})
            assert response.status_code == 400
            error_response = response.get_json()["errors"]
            assert all(field in error_response for field in ["euro_amount", "fixing_price", "fee_amount", "gold_grams"])
