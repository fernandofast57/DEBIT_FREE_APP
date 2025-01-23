
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from app.models import db
import re

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    two_factor_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relazioni
    transactions = db.relationship('Transaction', back_populates='user')
    kyc_documents = db.relationship('KYCDetail', back_populates='user', foreign_keys='KYCDetail.user_id')
    money_account = db.relationship('MoneyAccount', back_populates='user', uselist=False)
    gold_account = db.relationship('GoldAccount', back_populates='user', uselist=False)

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('Email non può essere vuoto')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Email non valido')
        return email

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username non può essere vuoto')
        if len(username) < 3:
            raise ValueError('Username deve essere almeno di 3 caratteri')
        return username
