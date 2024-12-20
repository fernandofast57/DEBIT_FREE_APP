
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
