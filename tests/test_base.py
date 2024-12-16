
import pytest
from app import create_app, db

class BaseTest:
    @pytest.fixture(autouse=True)
    async def setup(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        
        async with self.app.app_context():
            await db.create_all()
            yield
            await db.drop_all()
            db.session.remove()

    @pytest.fixture
    def test_client(self):
        return self.app.test_client()
