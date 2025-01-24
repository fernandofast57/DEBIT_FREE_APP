import os
import sys
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
import jwt
from decimal import Decimal
from web3 import Web3
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount
from app.utils.monitoring.blockchain_monitor import BlockchainMonitor
from app.services.blockchain_service import BlockchainService
from app.services.gold.weekly_distribution import WeeklyGoldDistribution

# Add the project root to the path
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'BLOCKCHAIN_ENABLED': True
    })
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
async def test_db(app):
    """Provide test database session"""
    async with app.app_context():
        await db.create_all()
        yield db
        await db.session.remove()
        await db.drop_all()


@pytest.fixture
async def test_user(app, test_db):
    """Crea un utente di test con account money e gold"""
    async with app.app_context():
        user = User(username='test_user', email='test@example.com')
        user.money_account = MoneyAccount(balance=Decimal('1000.00'))
        user.gold_account = GoldAccount(balance=Decimal('0.00'))
        test_db.session.add(user)
        await test_db.session.commit()
        return user


@pytest.fixture
def distribution_service():
    """Provide WeeklyGoldDistribution service"""
    return WeeklyGoldDistribution()


@pytest.fixture
async def async_session(app):
    """Provide async database session with application context"""
    async with app.app_context():
        async with db.session() as session:
            yield session


@pytest.fixture
def auth_token(app, test_user):
    """Genera un token JWT valido per l'utente di test"""
    payload = {
        'user_id': test_user.id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload,
                       app.config['JWT_SECRET_KEY'],
                       algorithm='HS256')
    return f'Bearer {token}'


@pytest.fixture
def auth_headers(auth_token, test_user):
    """Fornisce gli headers di autenticazione completi"""
    return {
        'Authorization': auth_token,
        'X-User-Id': str(test_user.id),
        'Content-Type': 'application/json'
    }


@pytest.fixture
def mock_w3():
    """Mock completo per Web3 con tutte le funzionalità necessarie"""
    w3 = Mock(spec=Web3)
    w3.eth = Mock()
    w3.eth.get_block_number = Mock(return_value=12345)
    w3.eth.wait_for_transaction_receipt = Mock(return_value=Mock(
        status=1, transactionHash=b'0x123', blockNumber=12345))
    w3.eth.get_transaction_count = Mock(return_value=0)
    w3.eth.send_raw_transaction = Mock(return_value=b'0x123')
    w3.eth.contract = Mock()
    w3.is_connected = Mock(return_value=True)
    w3.eth.gas_price = 20000000000
    w3.eth.chain_id = 80001
    w3.eth.account = Mock()
    w3.eth.account.sign_transaction = Mock(
        return_value=Mock(rawTransaction=b'0x456', hash=b'0x123'))

    # Aggiungi mock per eventi blockchain
    w3.eth.get_logs = Mock(return_value=[{
        'args': {
            'user': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'amount': 1000000000000000000,  # 1 ETH in wei
            'timestamp': int(datetime.utcnow().timestamp())
        }
    }])

    return w3


@pytest.fixture
async def blockchain_service(mock_w3):
    """Servizio blockchain configurato per i test"""
    service = BlockchainService()
    service.w3 = mock_w3
    service.contract = Mock()
    service.contract.functions = Mock()
    service.contract.functions.transfer = Mock()
    service.contract.functions.transfer().transact = Mock(
        return_value=b'0x123')
    service.account = Mock(
        address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        privateKey=b'0x123')
    return service


@pytest.fixture
def blockchain_monitor(mock_w3):
    """Monitor blockchain configurato per i test"""
    monitor = BlockchainMonitor(mock_w3)
    monitor.last_processed_block = 12344  # Un blocco prima del corrente
    return monitor


def get_test_rpc_url():
    """URL RPC per testing"""
    return "http://0.0.0.0:8545"
