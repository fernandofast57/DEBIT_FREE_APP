
from flask import Blueprint, request, jsonify
from app.services.workflow_service import WorkflowService
from app.middleware.security import require_auth, require_operator
from decimal import Decimal

workflow_bp = Blueprint('workflow', __name__)
workflow_service = WorkflowService()

@workflow_bp.route('/workflow/start/<int:transaction_id>', methods=['POST'])
@require_operator
async def start_workflow(transaction_id: int):
    try:
        result = await workflow_service.start_approval_workflow(transaction_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@workflow_bp.route('/workflow/step/<int:transaction_id>', methods=['POST'])
@require_operator
async def process_step(transaction_id: int):
    try:
        data = request.get_json()
        step = data.get('step')
        action = data.get('action')
        notes = data.get('notes')
        
        result = await workflow_service.process_step(transaction_id, step, action, notes)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@workflow_bp.route('/workflow/transform/<int:transaction_id>', methods=['POST'])
@require_operator
async def process_transformation(transaction_id: int):
    try:
        data = request.get_json()
        fixing_price = Decimal(data.get('fixing_price'))
        
        result = await workflow_service.process_weekly_transformation(
            transaction_id, fixing_price)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
