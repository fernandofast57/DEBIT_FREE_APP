
from flask import Blueprint, jsonify, request
from app.services.accounting_service import AccountingService
from app.utils.auth import auth_required
from app.utils.audit_logger import require_operator_approval

bp = Blueprint('accounting', __name__)
accounting_service = AccountingService()

@bp.route('/balance', methods=['GET'])
@auth_required
@require_operator_approval
def get_balance():
    """Get user's account balance"""
    return jsonify({
        "gold_balance": 100.0,
        "money_balance": 1000.0,
        "status": "active"
    }), 200

@bp.route('/inventory', methods=['GET'])
@auth_required
def get_inventory():
    return jsonify(accounting_service.get_inventory_summary())
