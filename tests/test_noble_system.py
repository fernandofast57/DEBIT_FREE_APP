
import pytest
from decimal import Decimal
from app.models.models import User, NobleRank, NobleRelation
from app.config.constants import STATUS_VERIFIED

def test_noble_rank_creation(app, client):
    """Test noble rank creation and verification"""
    with app.app_context():
        noble_rank = NobleRank(
            rank_name='bronze',
            bonus_rate=Decimal('0.005'),
            min_investment=Decimal('1000.00'),
            level=1
        )
        assert noble_rank.rank_name == 'bronze'
        assert noble_rank.level == 1

def test_noble_relation_verification(app, client):
    """Test noble relation verification process"""
    with app.app_context():
        user = User(
            username='test_noble',
            email='noble@test.com',
            password_hash='test_hash'
        )
        relation = NobleRelation(
            user=user,
            verification_status='to_be_verified'
        )
        assert relation.verification_status == 'to_be_verified'
