
import pytest
from decimal import Decimal
from app.models import User, NobleRank, Transaction
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create noble ranks
        ranks = [
            NobleRank(rank_name='Bronze', min_investment=Decimal('0'), bonus_rate=Decimal('0.001')),
            NobleRank(rank_name='Silver', min_investment=Decimal('5000'), bonus_rate=Decimal('0.002')),
            NobleRank(rank_name='Gold', min_investment=Decimal('10000'), bonus_rate=Decimal('0.003'))
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
            email='test@noble.com',
            blockchain_address='0x123...',
            total_investment=Decimal('0')
        )
        db.session.add(user)
        await db.session.commit()
        
        # Test initial rank
        assert user.noble_rank.rank_name == 'Bronze'
        
        # Test rank upgrade
        user.total_investment = Decimal('5000')
        await db.session.commit()
        assert user.noble_rank.rank_name == 'Silver'
        
        # Test highest rank
        user.total_investment = Decimal('10000')
        await db.session.commit()
        assert user.noble_rank.rank_name == 'Gold'

@pytest.mark.asyncio
async def test_noble_bonus_calculation(app):
    async with app.app_context():
        user = User(
            email='test@noble.com',
            blockchain_address='0x123...',
            total_investment=Decimal('5000')
        )
        db.session.add(user)
        await db.session.commit()
        
        investment_amount = Decimal('1000')
        bonus = user.noble_rank.calculate_bonus(investment_amount)
        expected_bonus = investment_amount * Decimal('0.002')  # Silver rank bonus
        assert bonus == expected_bonus

@pytest.mark.asyncio
async def test_noble_rank_requirements(app):
    async with app.app_context():
        ranks = NobleRank.query.order_by(NobleRank.min_investment).all()
        assert len(ranks) == 3
        assert ranks[0].rank_name == 'Bronze'
        assert ranks[1].rank_name == 'Silver'
        assert ranks[2].rank_name == 'Gold'
