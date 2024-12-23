
import pytest
from decimal import Decimal
from app.models import User, NobleRank, NobleRelation, Transaction
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create noble ranks according to glossary
        ranks = [
            NobleRank(rank_name='Bronze', min_investment=Decimal('0'), bonus_rate=Decimal('0.007'), level=1),
            NobleRank(rank_name='Silver', min_investment=Decimal('5000'), bonus_rate=Decimal('0.005'), level=2),
            NobleRank(rank_name='Gold', min_investment=Decimal('10000'), bonus_rate=Decimal('0.005'), level=3)
        ]
        db.session.add_all(ranks)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.mark.asyncio
async def test_noble_rank_assignment(app):
    async with app.app_context():
        user = User(
            username='test_noble',
            email='test@noble.com',
            password_hash='test123',
            blockchain_address='0x123...'
        )
        db.session.add(user)
        await db.session.commit()
        
        noble_relation = NobleRelation(
            user_id=user.id,
            noble_rank_id=1,
            verification_status='to_be_verified'
        )
        db.session.add(noble_relation)
        await db.session.commit()
        
        assert noble_relation.verification_status == 'to_be_verified'
        noble_relation.verification_status = 'verified'
        await db.session.commit()
        assert noble_relation.verification_status == 'verified'

@pytest.mark.asyncio
async def test_noble_bonus_calculation(app):
    async with app.app_context():
        user = User(
            username='test_noble',
            email='test@noble.com',
            password_hash='test123',
            blockchain_address='0x123...'
        )
        db.session.add(user)
        await db.session.commit()
        
        noble_relation = NobleRelation(
            user_id=user.id,
            noble_rank_id=2,  # Silver rank
            verification_status='verified'
        )
        db.session.add(noble_relation)
        await db.session.commit()
        
        investment_amount = Decimal('1000')
        bonus_rate = Decimal('0.005')  # Silver rank bonus
        expected_bonus = investment_amount * bonus_rate
        
        rank = await NobleRank.query.get(2)
        actual_bonus = rank.bonus_rate * investment_amount
        assert actual_bonus == expected_bonus
