
from flask import Blueprint, jsonify
from app.utils.auth import auth_required
from app.utils.validation_report import ValidationReport
from app.services.blockchain_service import BlockchainService
from app.services.batch_collection_service import BatchCollectionService

system_bp = Blueprint('system', __name__)

@system_bp.route('/status', methods=['GET'])
@auth_required
async def system_status():
    validator = ValidationReport()
    report = await validator.generate_report()
    
    # Analyze components health
    components_health = {
        'blockchain': report['blockchain'].get('connection', False),
        'batch_system': not bool(report['batch_system'].get('error')),
        'structure': all(
            all(item.values()) 
            for item in report['structure'].values() 
            if isinstance(item, dict)
        )
    }
    
    # Overall system health
    system_health = all(components_health.values())
    
    return jsonify({
        'status': 'operational' if system_health else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'components': components_health,
        'details': report
    })

@system_bp.route('/validate', methods=['GET'])
@auth_required
async def validate_system():
    validator = ValidationReport()
    report = await validator.generate_report()
    
    # Validate all subsystems
    validation_status = {
        'models': report['structure']['models'],
        'services': report['structure']['services'],
        'blockchain': report['blockchain'],
        'batch_processing': report['batch_system'],
        'security': report['structure']['security'],
        'noble_system': report['structure']['noble_system']
    }
    
    return jsonify({
        'validation_status': validation_status,
        'timestamp': datetime.utcnow().isoformat(),
        'glossary_compliance': all(
            all(component.values()) 
            for component in validation_status.values() 
            if isinstance(component, dict)
        )
    })
from flask import Blueprint, jsonify
from app.utils.monitoring import system_monitor
from flask_login import login_required

bp = Blueprint('system', __name__)

@bp.route('/metrics', methods=['GET'])
@login_required
def get_system_metrics():
    """Get system performance metrics"""
    return jsonify(system_monitor.get_metrics())

@bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({'status': 'healthy'})

async def status():
    """Async status check endpoint"""
    return jsonify({"status": "ok"})
from flask import Blueprint, jsonify
from app.utils.security import admin_required

mobile_admin = Blueprint('mobile_admin', __name__)

@mobile_admin.route('/admin/dashboard/mobile', methods=['GET'])
@admin_required
def mobile_dashboard():
    return jsonify({
        'active_users': get_active_users_count(),
        'daily_transactions': get_daily_transactions(),
        'system_health': get_system_health()
    })
from flask import Blueprint, jsonify

system_bp = Blueprint('system', __name__)

@system_bp.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "operational"}), 200
