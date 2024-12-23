
"""
Test del Sistema Nobiliare
-------------------------
Verifica le funzionalità del sistema di ranghi nobiliari e relazioni.
"""

import pytest
from app.models.models import User, NobleRank, NobleRelation
from app.services.noble_rank_service import NobleRankService

@pytest.mark.asyncio
async def test_noble_rank_creation():
    """Verifica la creazione corretta di un rango nobiliare"""
    noble_rank = NobleRank(
        rank_name="Conte",
        bonus_rate=0.007,
        min_investment=5000.00,
        level=1
    )
    assert noble_rank.rank_name == "Conte"
    assert float(noble_rank.bonus_rate) == 0.007

@pytest.mark.asyncio
async def test_noble_relation_verification():
    """Verifica il processo di verifica delle relazioni nobiliari"""
    relation = NobleRelation(
        verification_status='to_be_verified',
        document_type='passport',
        document_number='AB123456'
    )
    assert relation.verification_status == 'to_be_verified'
