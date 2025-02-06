from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy.orm import validates
import re
from . import db
from .notification import Notification
from app.middleware.class_validator_middleware import validate_class_names

class UserRole:
    USER = 'user'
    ADMIN = 'admin'
    OPERATOR = 'operator'

class KYCStatus:
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    TO_VERIFY = 'to_verify'

@validate_class_names()
class User(UserMixin, db.Model):
    """User model representing platform users with authentication and personal details"""
    __tablename__ = 'users'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Unique identifiers
    customer_code = db.Column(db.String(50), unique=True, nullable=False, 
                            comment='Unique customer identifier code')
    email = db.Column(db.String(120), unique=True, nullable=False, 
                     comment='User email address')

    # Authentication fields
    password_hash = db.Column(db.String(128), nullable=False, 
                            comment='Hashed password')
    two_factor_secret = db.Column(db.String(32), nullable=True, 
                                 comment='2FA secret key')
    two_factor_enabled = db.Column(db.Boolean, default=False, 
                                 comment='2FA enabled status')

    # Personal information
    name = db.Column(db.String(100), nullable=False, 
                    comment='Full name of user')
    tax_code = db.Column(db.String(16), unique=True, nullable=False, 
                        comment='Tax identification code')

    # Status and role
    kyc_status = db.Column(db.String(20), nullable=False, default=KYCStatus.PENDING,
                          comment='KYC verification status')
    role = db.Column(db.String(20), nullable=False, default=UserRole.USER,
                    comment='User role in the system')
    is_active = db.Column(db.Boolean, default=True, 
                         comment='Account active status')

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                          comment='Account creation timestamp')
    last_login = db.Column(db.DateTime, nullable=True,
                          comment='Last login timestamp')

    # Relationships
    transactions = db.relationship('Transaction', back_populates='user')
    kyc_documents = db.relationship('KYCDetail', back_populates='user', 
                                  foreign_keys='KYCDetail.user_id')
    euro_account = db.relationship('EuroAccount', back_populates='user', 
                                 uselist=False)
    gold_account = db.relationship('GoldAccount', back_populates='user', 
                                 uselist=False)

    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if not email:
            raise ValueError('Email cannot be empty')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Invalid email format')
        return email

    @validates('customer_code')
    def validate_customer_code(self, key, code):
        """Validate customer code format"""
        if not code:
            raise ValueError('Customer code cannot be empty')
        if len(code) < 5:
            raise ValueError('Customer code must be at least 5 characters')
        return code

    @validates('tax_code')
    def validate_tax_code(self, key, code):
        """Validate tax code format"""
        if not code:
            raise ValueError('Tax code cannot be empty')
        if len(code) != 16:
            raise ValueError('Tax code must be 16 characters')
        return code.upper()

    def __repr__(self):
        return f'<User {self.email}>'


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    GOLD_PURCHASE = "gold_purchase"
    GOLD_SALE = "gold_sale"


@validate_class_names()
class EuroAccount(db.Model):
    __tablename__ = 'euro_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=0.00)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='euro_account')

    def __repr__(self):
        return f"<EuroAccount User {self.user_id} Balance {self.balance}>"


@validate_class_names()
class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=4),
                        default=Decimal('0.0000'))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    blockchain_verified = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='gold_account')

    def __repr__(self):
        return f"<GoldAccount User {self.user_id} Balance {self.balance}>"


@validate_class_names()
class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    payment_method = db.Column(db.String(50), default='bank_transfer')
    processing_fee = db.Column(db.Numeric(precision=10, scale=4), default=0)
    net_amount = db.Column(db.Numeric(precision=10, scale=4))
    status = db.Column(db.String(20), default='pending')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))

    user = db.relationship('User', back_populates='transactions')

    @validates('amount')
    def validate_amount(self, key, amount):
        if amount <= 0:
            raise ValueError('Amount must be greater than zero')
        return amount

    def __repr__(self):
        return f"<Transaction {self.amount} ({self.transaction_type})>"


@validate_class_names()
class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='money_account')

    def __repr__(self):
        return f"<MoneyAccount User {self.user_id} Balance {self.balance}>"


@validate_class_names()
class GoldTracking(db.Model):
    __tablename__ = 'gold_tracking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    iban = db.Column(db.String(27), nullable=False)
    status = db.Column(db.String(20), default='pending')
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='gold_tracking')


@validate_class_names()
class KYCDetail(db.Model):
    __tablename__ = 'kyc_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_number = db.Column(db.String(100), nullable=False)
    document_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    verification_date = db.Column(db.DateTime, nullable=True)
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified_by = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            nullable=True)
    notes = db.Column(db.Text)

    user = db.relationship('User',
                           foreign_keys=[user_id],
                           back_populates='kyc_documents')
    verifier = db.relationship('User',
                               foreign_keys=[verified_by],
                               backref='kyc_verifications')


@validate_class_names()
class GoldTransformation(db.Model):
    __tablename__ = 'gold_transformations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    euro_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    gold_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    fixing_price = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    blockchain_tx_hash = db.Column(db.String(66), nullable=True)
    blockchain_status = db.Column(db.String(20), default='pending')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='gold_transformations')


@validate_class_names()
class BonusRate(db.Model):
    __tablename__ = 'bonus_rates'

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, unique=True)
    rate = db.Column(db.Numeric(precision=5, scale=4), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    @staticmethod
    def get_rate(level):
        rate = BonusRate.query.filter_by(level=level).first()
        return Decimal(str(rate.rate)) if rate else Decimal('0')


@validate_class_names()
class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'

    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            nullable=False)
    referred_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            nullable=False)
    level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    referrer = db.relationship('User',
                               foreign_keys=[referrer_id],
                               backref='referrals_made')
    referred = db.relationship('User',
                               foreign_keys=[referred_id],
                               backref='referral_info')

    __table_args__ = (db.UniqueConstraint('referrer_id',
                                          'referred_id',
                                          name='unique_referral'), )


@validate_class_names()
class Parameter(db.Model):
    __tablename__ = 'parameters'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)


@validate_class_names()
class GoldBar(db.Model):
    __tablename__ = 'gold_bars'

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    weight = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    purity = db.Column(db.Numeric(precision=5, scale=2), nullable=False)
    purchase_price = db.Column(db.Numeric(precision=10, scale=2),
                               nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GoldBar Serial {self.serial_number} Weight {self.weight}>"


@validate_class_names()
class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='bonus_transactions')

    def __repr__(self):
        return f"<BonusTransaction User {self.user_id} Amount {self.amount}>"


@validate_class_names()
class GoldReward(db.Model):
    __tablename__ = 'gold_rewards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_amount = db.Column(db.Numeric(precision=10, scale=4),
                              nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='gold_rewards')

    def __repr__(self):
        return f"<GoldReward User {self.user_id} Amount {self.reward_amount}>"


@validate_class_names()
class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        doc="Nome del titolo nobiliare (es. Bronze, Silver, Gold)")
    level = db.Column(db.Integer,
                      unique=True,
                      nullable=False,
                      doc="Livello gerarchico del titolo (1, 2, 3)")
    bonus_rate_id = db.Column(
        db.Integer,
        db.ForeignKey('bonus_rates.id'),
        nullable=True,
        doc="Chiave esterna a BonusRate")  # Relazione con BonusRate
    description = db.Column(db.String(200),
                            doc="Descrizione opzionale del titolo")

    bonus_rate = db.relationship('BonusRate',
                                 backref='noble_ranks')  # Relazione SQLAlchemy

    def __repr__(self):
        return f"<NobleRank {self.name} (Level {self.level})>"

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
from enum import Enum
from app.models import db