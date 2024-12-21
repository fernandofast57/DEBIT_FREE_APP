
from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.auth import admin_required, manager_required
from app.services.weekly_processing_service import WeeklyProcessingService

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@manager_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/gold-distribution')
@login_required
@admin_required
def gold_distribution():
    return render_template('admin/gold_distribution.html')

@admin_bp.route('/network-overview')
@login_required
def network_overview():
    return render_template('admin/network_overview.html')
