from datetime import datetime
from decimal import Decimal
from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import event

db = SQLAlchemy()


# ---------------------------------------
# ✅ Modello User (Utente)
# ---------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bonus_transactions = relationship('BonusTransaction', back_populates='user')
    # Add overlaps to fix the backref conflict
    rewards = relationship('GoldReward', back_populates='user', overlaps="gold_rewards")
    gold_rewards = relationship('GoldReward', back_populates='user')

    # Relazioni uno-a-uno
    money_account = db.relationship('MoneyAccount', back_populates='user', uselist=False)
    gold_account = db.relationship('GoldAccount', back_populates='user', uselist=False)

    # Relazioni uno-a-molti
    transactions = db.relationship('Transaction', back_populates='user')
    gold_transformations = db.relationship('GoldTransformation', back_populates='user')
    noble_relations = db.relationship('NobleRelation', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------------------------------
# ✅ Modello MoneyAccount (Conto in Denaro)
# ---------------------------------------
class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(precision=10, scale=2), default=Decimal('0.00'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='money_account')

    def __repr__(self):
        return f"<MoneyAccount {self.balance}>"


# ---------------------------------------
# ✅ Modello GoldAccount (Conto Oro)
# ---------------------------------------
class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'

    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(precision=10, scale=4), default=Decimal('0.0000'))
    pao_active = db.Column(db.Boolean, default=False)
    ppo_active = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='gold_account')

    allocations = db.relationship('GoldAllocation', back_populates='gold_account')

    def __repr__(self):
        return f"<GoldAccount {self.user.username}, {self.balance:.4f}g>"


# ---------------------------------------
# ✅ Modello NobleRank (Grado Nobiliare)
# ---------------------------------------
class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'

    id = db.Column(db.Integer, primary_key=True)
    rank_name = db.Column(db.String(50), nullable=False, unique=True)
    bonus_rate = db.Column(db.Numeric(precision=5, scale=4), nullable=False)
    min_investment = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<NobleRank {self.rank_name}>"


# ---------------------------------------
# ✅ Modello NobleRelation (Relazione Nobiliare)
# ---------------------------------------
class NobleRelation(db.Model):
    __tablename__ = 'noble_relations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    noble_rank_id = db.Column(db.Integer, db.ForeignKey('noble_ranks.id'), nullable=False)
    verification_status = db.Column(
        Enum('to_be_verified', 'verified', 'rejected', name='verification_status_enum'), 
        default='to_be_verified'
    )
    verification_date = db.Column(db.DateTime)
    document_type = db.Column(db.String(50))
    document_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='noble_relations')
    noble_rank = db.relationship('NobleRank')

    def __repr__(self):
        return f"<NobleRelation {self.verification_status}>"


# ---------------------------------------
# ✅ Modello Transaction (Transazioni)
# ---------------------------------------
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    status = db.Column(
        Enum('to_be_verified', 'verified', 'rejected', name='transaction_status_enum'),
        default='to_be_verified'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='transactions')

    def __repr__(self):
        return f"<Transaction {self.type} - {self.amount}>"


# ---------------------------------------
# ✅ Modello GoldTransformation (Conversione Oro)
# ---------------------------------------
class GoldTransformation(db.Model):
    __tablename__ = 'gold_transformations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    euro_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    gold_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    fixing_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    fee_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='gold_transformations')

    def __repr__(self):
        return f"<GoldTransformation {self.gold_grams}g>"


# ---------------------------------------
# ✅ Modello GoldBar (Lingotto d'Oro)
# ---------------------------------------
class GoldBar(db.Model):
    __tablename__ = 'gold_bars'

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    weight_grams = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    status = db.Column(
        Enum('available', 'reserved', 'distributed', name='gold_bar_status_enum'), 
        default='available'
    )
    location = db.Column(db.String(100))

    allocations = db.relationship('GoldAllocation', back_populates='gold_bar')

    def __repr__(self):
        return f"<GoldBar {self.serial_number}>"


# ---------------------------------------
# ✅ Modello GoldAllocation (Allocazione Oro)
# ---------------------------------------
class GoldAllocation(db.Model):
    __tablename__ = 'gold_allocations'

    id = db.Column(db.Integer, primary_key=True)
    grams_allocated = db.Column(db.Numeric(precision=10, scale=4), nullable=False)

    gold_bar_id = db.Column(db.Integer, db.ForeignKey('gold_bars.id'))
    gold_account_id = db.Column(db.Integer, db.ForeignKey('gold_accounts.id'))

    gold_bar = db.relationship('GoldBar', back_populates='allocations')
    gold_account = db.relationship('GoldAccount', back_populates='allocations')

    def __repr__(self):
        return f"<GoldAllocation {self.grams_allocated}g>"

# ---------------------------------------
# ✅ Modello GoldReward (Premi in Oro)
# ---------------------------------------
class GoldReward(db.Model):
    __tablename__ = 'gold_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='gold_rewards')

    def __repr__(self):
        return f"<GoldReward {self.amount}>"

# ---------------------------------------
# ✅ Modello BonusTransaction (Transazioni Bonus)
# ---------------------------------------
class BonusTransaction(db.Model):
    __tablename__ = 'bonus_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)
    transaction_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='bonus_transactions')
    
    __table_args__ = {'extend_existing': True}