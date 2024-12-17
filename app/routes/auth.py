
from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import User
from app.models import MoneyAccount, GoldAccount
from werkzeug.security import generate_password_hash
from decimal import Decimal

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('blockchain_address'):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
    
    user = User(
        email=data['email'],
        blockchain_address=data['blockchain_address']
    )
    
    try:
        db.session.add(user)
        db.session.flush()
        
        # Create associated accounts
        money_account = MoneyAccount(user_id=user.id, balance=Decimal('0'))
        gold_account = GoldAccount(user_id=user.id, balance=Decimal('0'))
        
        db.session.add_all([money_account, gold_account])
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'blockchain_address': user.blockchain_address
        }
    }), 200

@auth_bp.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    
    if not data or not data.get('user_id'):
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400
        
    user = User.query.get(data['user_id'])
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
    return jsonify({
        'status': 'success',
        'message': 'User verified',
        'verified': True
    }), 200
