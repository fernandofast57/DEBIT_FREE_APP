
from typing import Any, Dict
from decimal import Decimal
import pytest

def get_test_auth_headers():
    return {
        'X-User-Id': '123',
        'Authorization': 'Bearer test-token'
    }

def create_test_user(db_session) -> Dict[str, Any]:
    """Helper to create a test user with accounts"""
    from app.models.models import User, MoneyAccount, GoldAccount
    
    user = User(
        email="test@example.com",
        username="test_user",
        blockchain_address="0x123..."
    )
    money_account = MoneyAccount(balance=Decimal('1000.00'))
    gold_account = GoldAccount(balance=Decimal('0'))
    
    user.money_account = money_account
    user.gold_account = gold_account
    
    db_session.add(user)
    db_session.commit()
    
    return {
        "user": user,
        "money_account": money_account,
        "gold_account": gold_account
    }
def get_test_auth_headers():
    """Helper function to generate test authentication headers"""
    return {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }
def get_test_auth_headers():
    """Generate test authentication headers"""
    return {
        'Authorization': 'Bearer TEST_TOKEN',
        'Content-Type': 'application/json'
    }
