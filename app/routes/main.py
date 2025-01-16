
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.utils.auth import admin_required, operator_required
from app.services.accounting_service import AccountingService
from app.services.notification_service import NotificationService

bp = Blueprint('main', __name__)
accounting_service = AccountingService()
notification_service = NotificationService()

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.is_operator:
        return redirect(url_for('main.operator_dashboard'))
    return redirect(url_for('main.client_dashboard'))

@bp.route('/client/dashboard')
@login_required
def client_dashboard():
    transactions = accounting_service.get_user_transactions(current_user.id)
    gold_balance = current_user.gold_account.balance
    euro_balance = current_user.money_account.balance
    rewards = accounting_service.get_user_rewards(current_user.id)
    
    return render_template('client/dashboard.html',
                         transactions=transactions,
                         gold_balance=gold_balance,
                         euro_balance=euro_balance,
                         rewards=rewards)

@bp.route('/operator/dashboard')
@login_required
@operator_required
def operator_dashboard():
    pending_transfers = accounting_service.get_pending_transfers()
    weekly_gold_stats = accounting_service.get_weekly_gold_stats()
    return render_template('operator/dashboard.html',
                         pending_transfers=pending_transfers,
                         weekly_gold_stats=weekly_gold_stats)

@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    system_stats = accounting_service.get_system_stats()
    users = accounting_service.get_all_users()
    notifications = notification_service.get_admin_notifications()
    return render_template('admin/dashboard.html',
                         system_stats=system_stats,
                         users=users,
                         notifications=notifications)
