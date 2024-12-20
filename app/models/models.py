
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    
    # Relationships
    money_account: Mapped["MoneyAccount"] = relationship(back_populates="user")
    gold_account: Mapped["GoldAccount"] = relationship(back_populates="user")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user")
    noble_rank: Mapped[Optional["NobleRank"]] = relationship(back_populates="user")

class MoneyAccount(db.Model):
    __tablename__ = 'money_accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    balance: Mapped[float] = mapped_column(default=0.0)
    
    user: Mapped["User"] = relationship(back_populates="money_account")

class GoldAccount(db.Model):
    __tablename__ = 'gold_accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    balance: Mapped[float] = mapped_column(default=0.0)
    
    user: Mapped["User"] = relationship(back_populates="gold_account")

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    amount: Mapped[float]
    transaction_type: Mapped[str]
    status: Mapped[str]
    timestamp: Mapped[str]
    
    user: Mapped["User"] = relationship(back_populates="transactions")

class NobleRank(db.Model):
    __tablename__ = 'noble_ranks'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'), unique=True)
    rank: Mapped[str]
    points: Mapped[int] = mapped_column(default=0)
    
    user: Mapped["User"] = relationship(back_populates="noble_rank")
class GoldBar(db.Model):
    __tablename__ = 'gold_bars'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    serial_number: Mapped[str] = mapped_column(unique=True)
    weight_grams: Mapped[float]
    location: Mapped[str]
    status: Mapped[str]  # in_vault, redeemed, reserved
    certification: Mapped[str]
    
    participations: Mapped[List["GoldBarParticipation"]] = relationship(back_populates="gold_bar")

class GoldBarParticipation(db.Model):
    __tablename__ = 'gold_bar_participations'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    bar_id: Mapped[int] = mapped_column(db.ForeignKey('gold_bars.id'))
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    share_grams: Mapped[float]
    participation_code: Mapped[str] = mapped_column(unique=True)
    
    gold_bar: Mapped["GoldBar"] = relationship(back_populates="participations")
    user: Mapped["User"] = relationship(back_populates="bar_participations")

class CustomerKYC(db.Model):
    __tablename__ = 'customer_kyc'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'), unique=True)
    verification_status: Mapped[str]  # pending, approved, rejected
    document_type: Mapped[str]
    document_number: Mapped[str]
    expiry_date: Mapped[str]
    verification_date: Mapped[str]
    verified_by: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
class GoldReward(db.Model):
    __tablename__ = 'gold_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gold_amount = db.Column(db.Numeric(precision=10, scale=4), nullable=False)  # In grams
    reward_type = db.Column(db.String(50), nullable=False)  # 'structure' or 'achievement'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='gold_rewards')
