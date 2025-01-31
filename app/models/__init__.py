from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .noble_system import NobleRank
from .models import (
    EuroAccount,
    GoldAccount,
    Transaction,
    NobleRelation,
    GoldBar,
    Parameter,
    BonusTransaction,
    KYCDetail,
    GoldTracking,
    BonusRate,
    GoldReward
)
from .notification import Notification

__all__ = [
    'db',
    'User',
    'EuroAccount',
    'GoldAccount',
    'Transaction',
    'NobleRank',
    'NobleRelation',
    'GoldBar',
    'Parameter',
    'BonusTransaction',
    'KYCDetail',
    'GoldTracking',
    'Notification',
    'BonusRate',
    'GoldReward'
]