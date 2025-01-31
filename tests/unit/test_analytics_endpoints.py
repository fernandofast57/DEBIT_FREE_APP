
import pytest
from decimal import Decimal
from app.models.models import User, ContoOro
from app.models.noble_system import NobleRank
from app.models.transaction import Transaction

@pytest.mark.asyncio
async def test_metrics_endpoint(test_client, test_db):
    # Setup test data
    user = User(username="test_user", email="test@example.com")
    conto_oro = ContoOro(balance=Decimal('100.00'))
    user.conto_oro = conto_oro
    test_db.add(user)
    await test_db.commit()

    response = await test_client.get('/api/v1/analytics/metrics')
    assert response.status_code == 200
    data = response.json
    assert 'total_users' in data
    assert 'total_gold' in data
    assert 'total_transactions' in data

@pytest.mark.asyncio
async def test_noble_distribution_endpoint(test_client, test_db):
    # Setup test data
    rank = NobleRank(level=1)
    user = User(username="noble_user", email="noble@example.com")
    user.noble_relation = rank
    test_db.add(user)
    await test_db.commit()

    response = await test_client.get('/api/v1/analytics/noble-distribution')
    assert response.status_code == 200
    data = response.json
    assert '1' in data  # Verifica presenza livello 1

@pytest.mark.asyncio
async def test_transaction_trends_endpoint(test_client, test_db):
    # Setup test data
    transaction = Transaction(amount=Decimal('50.00'))
    test_db.add(transaction)
    await test_db.commit()

    response = await test_client.get('/api/v1/analytics/transaction-trends')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) > 0
