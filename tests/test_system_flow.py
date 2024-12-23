
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.models import User, MoneyAccount, GoldAccount, Transaction, NobleRelation
from app import db

@pytest.mark.asyncio
async def test_complete_flow():
    """Test del flusso completo secondo il glossario"""
    # Setup
    user = User(
        username='test_user',
        email='test@example.com',
        password_hash='test123'
    )
    db.session.add(user)
    await db.session.flush()
    
    money_account = MoneyAccount(
        user_id=user.id,
        balance=Decimal('1000.00')
    )
    gold_account = GoldAccount(
        user_id=user.id,
        balance=Decimal('0')
    )
    db.session.add_all([money_account, gold_account])
    await db.session.commit()

    # Test transformation with correct status codes
    transformation_service = TransformationService()
    fixing_price = Decimal('1850.00')
    
    result = await transformation_service.transform_to_gold(
        user.id,
        fixing_price
    )
    
    assert result['status'] == 'verified'
    assert money_account.balance == Decimal('0')
    assert gold_account.balance > Decimal('0')

@pytest.mark.asyncio
async def test_noble_verification_flow():
    """Test del flusso di verifica noble"""
    user = User(
        username='noble_user',
        email='noble@example.com',
        password_hash='test123'
    )
    db.session.add(user)
    await db.session.flush()
    
    noble_relation = NobleRelation(
        user_id=user.id,
        noble_rank_id=1,
        verification_status='to_be_verified'
    )
    db.session.add(noble_relation)
    await db.session.commit()
    
    # Test status transitions
    assert noble_relation.verification_status == 'to_be_verified'
    noble_relation.verification_status = 'verified'
    await db.session.commit()
    assert noble_relation.verification_status == 'verified'
