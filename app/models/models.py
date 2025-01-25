from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db
from .user import User

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    GOLD_PURCHASE = "gold_purchase"
    GOLD_SALE = "gold_sale"

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))

    @validates('payment_method')
    def validate_payment_method(self, key, method):
        valid_methods = ['bank_transfer', 'credit_card', 'paypal']
        if method not in valid_methods:
            raise ValueError('Metodo di pagamento non valido')
        return method

    def calculate_net_amount(self):
        """Calcola l'importo netto dopo le commissioni"""
        self.net_amount = self.amount - self.processing_fee
        return self.net_amount

    user = db.relationship('User', back_populates='transactions')

    @validates('amount')
    def validate_amount(self, key, amount):
        if amount <= 0:
            raise ValueError('L\'importo deve essere maggiore di zero')
        return amount

    @validates('transaction_type')
    def validate_transaction_type(self, key, trans_type):
        if trans_type not in TransactionType:
            raise ValueError('Tipo transazione non valido')
        return trans_type

    def __repr__(self):
        return f"<Transaction {self.amount} ({self.transaction_type})>"


class BankTransfer(db.Model):
    __tablename__ = 'bank_transfers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    iban = db.Column(db.String(34), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='bank_transfers')

class Parameter(db.Model):
    __tablename__ = 'parameters'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Parameter {self.key} = {self.value}>"


class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='money_account')

    def __repr__(self):
        return f"<MoneyAccount User {self.user_id} Balance {self.balance}>"


class GoldTransformation(db.Model):
    __tablename__ = 'gold_transformations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    euro_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    gold_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    fixing_price = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    blockchain_tx_hash = db.Column(db.String(66), nullable=True)
    blockchain_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='gold_transformations')

    def __repr__(self):
        return f"<GoldTransformation User {self.user_id} Euro {self.euro_amount} Gold {self.gold_grams}>"


class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=0.00)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='gold_account')

    def __repr__(self):
        return f"<GoldAccount User {self.user_id} Balance {self.balance}>"


class KYCDetail(db.Model):
    __tablename__ = 'kyc_details'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(
        db.String(50), nullable=False)  # passport, id_card, drivers_license
    document_number = db.Column(db.String(100), nullable=False)
    document_url = db.Column(db.String(255))
    status = db.Column(db.String(20),
                       default='pending')  # pending, approved, rejected
    verification_date = db.Column(db.DateTime, nullable=True)
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified_by = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            nullable=True)
    notes = db.Column(db.Text)

    # Relazioni
    user = db.relationship('User',
                           foreign_keys=[user_id],
                           back_populates='kyc_documents')
    verifier = db.relationship('User',
                               foreign_keys=[verified_by],
                               backref='kyc_verifications')

    def __repr__(self):
        return f"<KYCDetail {self.id} - User {self.user_id} - Status {self.status}>"


class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    rank_name = db.Column(db.String(50), nullable=False)
    bonus_rate = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    min_investment = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<NobleRank {self.rank_name} (Bonus Rate: {self.bonus_rate})>"


class GoldAllocation(db.Model):
    __tablename__ = 'gold_allocations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grams_allocated = db.Column(db.Numeric(precision=10, scale=4),
                                nullable=False)
    date_allocated = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='gold_allocations')

    def __repr__(self):
        return f"<GoldAllocation User {self.user_id} Grams {self.grams_allocated}>"


class GoldBar(db.Model):
    __tablename__ = 'gold_bars'

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    weight = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    purity = db.Column(db.Numeric(precision=5, scale=2), nullable=False)
    purchase_price = db.Column(db.Numeric(precision=10, scale=2),
                               nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GoldBar Serial {self.serial_number} Weight {self.weight}>"


class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='bonus_transactions')

    def __repr__(self):
        return f"<BonusTransaction User {self.user_id} Amount {self.amount}>"


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


class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    noble_rank_id = db.Column(db.Integer,
                              db.ForeignKey('noble_ranks.id'),
                              nullable=False)
    verification_status = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', backref='noble_relations')
    noble_rank = db.relationship('NobleRank', backref='noble_relations')

    def __repr__(self):
        return f"<NobleRelation User {self.user_id} Rank {self.noble_rank_id}>"