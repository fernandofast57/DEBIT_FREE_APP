
from flask import Blueprint, jsonify, request
from app.services.accounting_service import AccountingService
from app.utils.auth import auth_required

bp = Blueprint('accounting', __name__)
accounting_service = AccountingService()

@bp.route('/balance', methods=['GET'])
def get_balance():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    return jsonify({"gold_balance": 0.0, "money_balance": 0.0}), 200

@bp.route('/inventory', methods=['GET'])
@auth_required
def get_inventory():
    return jsonify(accounting_service.get_inventory_summary())
