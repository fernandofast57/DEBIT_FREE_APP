
import pytest
from app.models import User, NobleRank
from app import create_app, db

@pytest.fixture
async def noble_app():
    app = create_app()
    async with app.app_context():
        await db.create_all()
        yield app
        await db.session.remove()
        await db.drop_all()

@pytest.mark.asyncio
async def test_noble_rank_assignment(noble_app):
    async with noble_app.app_context():
        user = User(email='test@noble.com', blockchain_address='0x123...')
        db.session.add(user)
        await db.session.commit()
        
        # Test initial rank
        assert user.noble_rank.rank_name == 'knight'
        
        # Test rank upgrade
        user.total_investment = 50000
        await db.session.commit()
        assert user.noble_rank.rank_name == 'baron'
