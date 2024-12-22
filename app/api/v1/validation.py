
from flask import Blueprint, jsonify
from app.utils.validation_report import ValidationReport

validation_bp = Blueprint('validation', __name__)

@validation_bp.route('/system/validate', methods=['GET'])
async def validate_system():
    validator = ValidationReport()
    report = await validator.generate_report()
    return jsonify(report)
