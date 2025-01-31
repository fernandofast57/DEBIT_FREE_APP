import pytest
from decimal import Decimal
from app.models.noble_system import NobleRelation
from app.services.noble_rank_service import NobleRankService

@pytest.mark.asyncio
async def test_sistema_nobile(test_client, test_db):
    """Verifica il sistema nobiliare secondo il glossario"""
    servizio = ServizioNobile(test_db)

    # Verifica LivelliReferral
    nobile = RelazioneNobile(
        livello=1,  # Primo livello referral
        stato_validazione='approvato'  # StatoValidazione
    )
    test_db.add(noble)
    await test_db.commit()

    # Verifica PremioReferral
    bonus_rate = await service.get_referral_rate(noble.level)
    assert bonus_rate == Decimal('0.007')  # 0.7% per livello 1