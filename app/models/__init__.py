from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Moved to a separate module to resolve circular import
# Initialize extensions
#login_manager = LoginManager()
#migrate = Migrate()
#
## Configure login manager
#login_manager.login_view = 'auth.login'
#login_manager.login_message_category = 'info'
#
## Import models after db initialization
#from .models import (
#    User,
#    MoneyAccount,
#    GoldAccount,
#    Transaction,
#    NobleRank,
#    NobleRelation,
#    GoldBar,
#    GoldAllocation,
#    Parameter,
#    BonusTransaction
#)
#
## Explicitly export
#__all__ = [
#    'db',
#    #'login_manager',  # Removed to resolve circular import
#    #'User',
#    #'MoneyAccount',
#    #'GoldAccount',
#    #'Transaction',
#    #'NobleRank',
#    #'NobleRelation',
#    #'GoldBar',
#    #'GoldAllocation',
#    #'Parameter',
#    #'BonusTransaction'
#]