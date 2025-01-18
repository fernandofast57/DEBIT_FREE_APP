from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import dei modelli
from .models import (
    User,
    MoneyAccount,
    GoldAccount,
    Transaction,
    NobleRank,
    NobleRelation,
    GoldBar,
    GoldAllocation,
    Parameter,
    BonusTransaction
)

# Esplicita gli elementi esportabili
__all__ = [
    'db',
    'login_manager',
    'User',
    'MoneyAccount', 
    'GoldAccount',
    'Transaction',
    'NobleRank',
    'NobleRelation',
    'GoldBar',
    'GoldAllocation',
    'Parameter',
    'BonusTransaction'
]
