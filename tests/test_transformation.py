
import pytest
from decimal import Decimal
from app.models.models import User, MoneyAccount, GoldAccount, GoldTransformation
from app.services.transformation_service import TransformationService

def test_valid_transformation(app, client):
    """Test valid transformation request"""
    response = client.post('/api/v1/transformations/transform', json={
        "euro_amount": 150.00,
        "fixing_price": 50.00,
        "fee_amount": 5.00,
        "gold_grams": 3.5
    })
    assert response.status_code == 200
    assert "Gold transformed successfully" in response.json["message"]

@pytest.mark.asyncio
async def test_invalid_euro_amount(app, client):
    """Test invalid euro amount validation"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": 50.00,
        "fixing_price": 50.00,
        "fee_amount": 5.00,
        "gold_grams": 3.5
    })
    assert response.status_code == 400
    assert "euro_amount" in response.json["errors"]

@pytest.mark.asyncio
async def test_invalid_fixing_price(app, client):
    """Test invalid fixing price validation"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": 150.00,
        "fixing_price": 0.00,
        "fee_amount": 5.00,
        "gold_grams": 3.5
    })
    assert response.status_code == 400
    assert "fixing_price" in response.json["errors"]

@pytest.mark.asyncio
async def test_invalid_fee_amount(app, client):
    """Test invalid fee amount validation"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": 150.00,
        "fixing_price": 50.00,
        "fee_amount": -1.00,
        "gold_grams": 3.5
    })
    assert response.status_code == 400
    assert "fee_amount" in response.json["errors"]

@pytest.mark.asyncio
async def test_invalid_gold_grams(app, client):
    """Test invalid gold grams validation"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": 150.00,
        "fixing_price": 50.00,
        "fee_amount": 5.00,
        "gold_grams": 0.00
    })
    assert response.status_code == 400
    assert "gold_grams" in response.json["errors"]

@pytest.mark.asyncio
async def test_missing_required_fields(app, client):
    """Test missing required fields validation"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": 150.00
    })
    assert response.status_code == 400
    assert "fixing_price" in response.json["errors"]
    assert "fee_amount" in response.json["errors"]
    assert "gold_grams" in response.json["errors"]

@pytest.mark.asyncio
async def test_extra_fields(app, client):
    """Test request with extra unexpected fields"""
    response = await client.post('/api/v1/transformations/transform', json={
        "euro_amount": 150.00,
        "fixing_price": 50.00,
        "fee_amount": 5.00,
        "gold_grams": 3.5,
        "unexpected_field": "extra_data"
    })
    assert response.status_code == 400
    assert "unexpected_field" in response.json["errors"]

@pytest.mark.asyncio
async def test_empty_payload(app, client):
    """Test empty payload validation"""
    response = await client.post('/api/v1/transformations/transform', json={})
    assert response.status_code == 400
    assert "euro_amount" in response.json["errors"]
    assert "fixing_price" in response.json["errors"]
    assert "fee_amount" in response.json["errors"]
    assert "gold_grams" in response.json["errors"]
