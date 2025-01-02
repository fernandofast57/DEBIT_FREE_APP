
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
import json
from datetime import datetime
from app.models import db, User, Transaction, Parameter
from app.services.blockchain_service import BlockchainService
from app.utils.cache.redis_manager import RedisManager
from app.services.noble_rank_service import NobleRankService

admin_bp = Blueprint('custom_admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/parameters', methods=['GET', 'POST'])
@login_required
@admin_required
def parameters():
    if request.method == 'POST':
        param = Parameter.query.first()
        if not param:
            param = Parameter()
            db.session.add(param)
        param.transformation_rate = request.form.get('transformation_rate', 1.0)
        param.commission_rate = request.form.get('commission_rate', 0.01)
        db.session.commit()
        flash('Parameters updated successfully', 'success')
        return redirect(url_for('admin.parameters'))
    
    params = Parameter.query.first()


@admin_bp.route('/noble-system')
@login_required
@admin_required
def noble_system():
    noble_service = NobleRankService()
    ranks = noble_service.get_all_ranks()
    return render_template('admin/noble_system.html', ranks=ranks)

@admin_bp.route('/blockchain')
@login_required
@admin_required
def blockchain():
    blockchain_service = BlockchainService()
    stats = blockchain_service.get_network_stats()
    return render_template('admin/blockchain.html', stats=stats)

@admin_bp.route('/api/system-status')
@login_required
@admin_required
def system_status():
    return jsonify({
        'last_update': datetime.utcnow().isoformat(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'pending_transactions': Transaction.query.filter_by(status='pending').count()
    })

@admin_bp.route('/api/refresh-cache', methods=['POST'])
@login_required
@admin_required
def refresh_cache():
    redis = RedisManager()
    redis.flush_all()
    return jsonify({'message': 'Cache refreshed successfully'})

@admin_bp.route('/api/blockchain-status')
@login_required
@admin_required
def blockchain_status():
    blockchain_service = BlockchainService()
    status = blockchain_service.check_connection()
    return jsonify({'status': 'connected' if status else 'disconnected'})

@admin_bp.route('/generate-report')
@login_required
@admin_required
def generate_report():
    # Generate system report
    report_data = {
        'users': User.query.count(),
        'transactions': Transaction.query.count(),
        'parameters': Parameter.query.first().to_dict()
    }
    
    return jsonify(report_data)

    return render_template('admin/parameters.html', params=params)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    transactions = Transaction.query.all()
    return render_template('admin/transactions.html', transactions=transactions)
