
from flask import Blueprint, jsonify
from app.utils.auth import auth_required
from app.utils.validation_report import ValidationReport
from app.services.blockchain_service import BlockchainService
from app.services.batch_collection_service import BatchCollectionService

bp = Blueprint('system', __name__)

@system_bp.route('/status', methods=['GET'])
@auth_required
async def system_status():
    validator = ValidationReport()
    status = await validator.generate_report()
    return jsonify({
        'status': 'operational' if all(status.values()) else 'degraded',
        'components': status
    })
