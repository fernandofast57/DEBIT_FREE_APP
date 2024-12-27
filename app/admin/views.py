
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models import db, User, Transaction
from app.models.models import Parameter

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
