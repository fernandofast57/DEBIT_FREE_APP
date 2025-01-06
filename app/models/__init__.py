from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inizializzazione delle estensioni
db = SQLAlchemy()
login_manager = LoginManager()

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
