
from flask import Blueprint, jsonify, request
from app.services.accounting_service import AccountingService
from app.utils.auth import auth_required
from decimal import Decimal

bp = Blueprint('accounting', __name__)
accounting_service = AccountingService()

@bp.route('/inventory', methods=['GET'])
@auth_required
def get_inventory():
    return jsonify(accounting_service.get_inventory_summary())

@bp.route('/gold/purchase', methods=['POST'])
@auth_required
def record_purchase():
    data = request.get_json()
    grams = Decimal(str(data['grams']))
    price = Decimal(str(data['price_per_gram']))
    
    inventory = accounting_service.record_gold_purchase(grams, price)
    return jsonify({
        'status': 'success',
        'inventory_id': inventory.id
    })
