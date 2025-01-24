# app/routes/auth.py
from flask import Blueprint, jsonify, request, current_app, render_template
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash
from decimal import Decimal
from functools import wraps

from app.models import db
from app.models import User, MoneyAccount, GoldAccount, Transaction
from app.utils.auth import AuthManager
from app.middleware.security import security
from app.services.two_factor_service import TwoFactorService
from app.services.kyc_service import KYCService
from config import Config

auth_bp = Blueprint('auth', __name__)
auth_manager = AuthManager(Config().SECRET_KEY)
two_factor_service = TwoFactorService()
kyc_service = KYCService()


def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)

    return decorated_function


# Registration and Basic Auth Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('blockchain_address'):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'message': 'Email already registered'
        }), 400

    try:
        user = User(email=data['email'],
                    blockchain_address=data['blockchain_address'])

        db.session.add(user)
        db.session.flush()

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
        return jsonify({
            'status': 'error',
            'message': 'Registration failed'
        }), 500


@auth_bp.route('/login', methods=['POST'])
@security.rate_limit('auth')
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    device_id = data.get('device_id')

    if not user_id or not device_id:
        return jsonify({'error': 'Missing required fields'}), 400

    if not auth_manager.is_valid_device(user_id, device_id):
        return jsonify({'error': 'Invalid device'}), 403

    token = auth_manager.generate_token(user_id, device_id)
    return jsonify({'token': token})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401

    if auth_manager.revoke_token(token):
        return jsonify({'message': 'Logged out successfully'})
    return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/login-status', methods=['GET'])
@login_required
def login_status():
    return jsonify({
        'status': 'success',
        'logged_in': current_user.is_authenticated,
        'is_admin': current_user.is_admin,
        'user': current_user.username
    })


# 2FA Routes
@auth_bp.route('/2fa/enable', methods=['POST'])
@login_required
async def enable_2fa():
    try:
        result = await two_factor_service.enable_2fa(current_user.id)
        return jsonify({
            'status': 'success',
            'qr_code': result['qr_code'],
            'message': 'Two-factor authentication enabled'
        }), 200
    except Exception as e:
        current_app.logger.error(f"2FA enable error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


@auth_bp.route('/2fa/verify', methods=['POST'])
@login_required
async def verify_2fa():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'status': 'error', 'message': 'Token required'}), 400

    if two_factor_service.verify_2fa(current_user.two_factor_secret,
                                     data['token']):
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'Invalid token'}), 400


# Admin Routes
@auth_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_transactions': Transaction.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)


@auth_bp.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@auth_bp.route('/admin/transactions')
@login_required
@admin_required
def transactions():
    transactions = Transaction.query.all()
    return render_template('admin/transactions.html',
                           transactions=transactions)


# KYC Routes
@auth_bp.route('/kyc/submit', methods=['POST'])
@login_required
async def submit_kyc():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        result = await kyc_service.submit_kyc(
            current_user.id,
            document_type=data['document_type'],
            document_number=data['document_number'],
            document_url=data.get('document_url'))
        return jsonify(result), 200 if result['status'] == 'success' else 400

    except Exception as e:
        current_app.logger.error(f"KYC submission error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


@auth_bp.route('/kyc/status', methods=['GET'])
@login_required
async def get_kyc_status():
    try:
        status = await kyc_service.get_user_kyc_status(current_user.id)
        return jsonify({'status': 'success', 'kyc_status': status}), 200
    except Exception as e:
        current_app.logger.error(f"KYC status check error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
