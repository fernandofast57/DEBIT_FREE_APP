from typing import Dict
from datetime import timedelta

# Status codes
STATUS_TO_BE_VERIFIED = 'to_be_verified'
STATUS_VERIFIED = 'verified'
STATUS_REJECTED = 'rejected'
STATUS_PENDING = 'pending'
STATUS_EXPIRED = 'expired'
STATUS_SUSPENDED = 'suspended'
STATUS_AVAILABLE = 'available'
STATUS_RESERVED = 'reserved'
STATUS_DISTRIBUTED = 'distributed'

# Tipi di operazione
TRANSACTION_TYPE_ACQUISTO = 'acquisto'
TRANSACTION_TYPE_VENDITA = 'vendita'
TRANSACTION_TYPE_TRASFERIMENTO = 'trasferimento'
TRANSACTION_TYPE_TRASFORMAZIONE = 'trasformazione'

# Noble ranks
RANGO_NOBILE = ['bronzo', 'argento', 'oro']  # RangoNobile from glossary


# Cache Timeout Constants
CACHE_TIMEOUT = 3600  # Default cache timeout in seconds
EXTENDED_CACHE_TIMEOUT = 86400  # 24 hours
SHORT_CACHE_TIMEOUT = 300  # 5 minutes
VOLATILE_CACHE_TIMEOUT = 60  # 1 minute

class TestConfig:
    """Test configuration class"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test_secret_key'
    WTF_CSRF_ENABLED = False