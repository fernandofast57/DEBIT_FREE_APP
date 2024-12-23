
"""
Test del Servizio di Trasformazione
----------------------------------
Verifica le funzionalità di conversione da euro a oro e viceversa.
"""

import pytest
from decimal import Decimal
from app.services.transformation_service import TransformationService
from app.models.models import User, MoneyAccount, GoldAccount

@pytest.mark.asyncio
async def test_transform_to_gold():
    """Verifica la trasformazione da euro a oro"""
    service = TransformationService()
    user = User(username="test_user", email="test@example.com")
    
    result = await service.transform_to_gold(
        user_id=user.id,
        fixing_price=Decimal('55.00')
    )
    
    assert result['status'] == 'verified'
    assert 'gold_grams' in result['transaction']
