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
def w3():
    provider = Web3.HTTPProvider('https://polygon-mumbai.infura.io/v3/YOUR-PROJECT-ID')
    w3 = Web3(provider)
    if not w3.is_connected():
        pytest.skip("Blocco della connessione blockchain non disponibile")
    return w3

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