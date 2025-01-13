import pytest
from app import create_app  # Assicura che create_app sia importato correttamente
from app.database import db
from app.models.models import User, MoneyAccount, GoldAccount  # Importa i modelli
from web3 import Web3
from app.utils.blockchain_monitor import BlockchainMonitor
from decimal import Decimal

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def populate_database(app):
    """Popola il database con dati di esempio prima di ciascun test."""
    with app.app_context():
        user = User(username='test_user', email='test@example.com')
        user.money_account = MoneyAccount(balance=Decimal('1000.00'))
        user.gold_account = GoldAccount(balance=Decimal('0.00'))
        db.session.add(user)
        db.session.commit()
        yield  # Consenti al test di eseguire
        db.session.remove()  # Rimuovi la sessione
        db.drop_all()  # Pulisci il database

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def mock_w3():
    w3 = Mock(spec=Web3)
    w3.eth = Mock()
    w3.eth.get_block_number = Mock(return_value=12345)
    w3.eth.wait_for_transaction_receipt = Mock(return_value=Mock(status=1))
    w3.is_connected = Mock(return_value=True)
    w3.eth.gas_price = 20000000000
    w3.eth.chain_id = 80001
    return w3

@pytest.fixture
async def blockchain_service(mock_w3):
    service = BlockchainService()
    service.w3 = mock_w3
    service.contract = Mock()
    service.account = Mock(address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
    return service

@pytest.fixture
def blockchain_monitor(w3):
    return BlockchainMonitor(w3)

@pytest.fixture
def auth_headers():
    return {
        'Authorization': 'Bearer valid-test-token',
        'X-User-Id': '123'
    }

def get_test_rpc_url():
    return "http://0.0.0.0:8545"  # Assicurati che l'URL RPC sia accessibile