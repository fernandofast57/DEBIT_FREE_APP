
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

from .models import User, MoneyAccount, GoldAccount, Transaction, NobleRank, NobleRelation, GoldBar, GoldAllocation, Parameter, BonusTransaction

__all__ = [
    'db',
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
