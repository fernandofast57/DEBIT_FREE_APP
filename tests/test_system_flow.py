
"""
Test del Flusso di Sistema
-------------------------
Verifica l'intero flusso operativo del sistema, dalla registrazione 
alla trasformazione dell'oro.
"""

import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount
from app.services.transformation_service import TransformationService

@pytest.mark.asyncio
async def test_complete_transformation_flow():
    """Verifica il flusso completo di trasformazione da euro a oro"""
    # Setup iniziale
    user = User(username="test_user", email="test@example.com")
    money_account = MoneyAccount(balance=Decimal('1000.00'))
    gold_account = GoldAccount(balance=Decimal('0.00'))
    
    # Verifica trasformazione
    service = TransformationService()
    result = await service.transform_to_gold(
        user_id=user.id,
        fixing_price=Decimal('50.00')
    )
    
    assert result['status'] == 'verified'
    assert float(gold_account.balance) > 0
