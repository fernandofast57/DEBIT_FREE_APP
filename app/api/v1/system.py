from flask import Blueprint, jsonify
from app.utils.monitoring.performance_monitor import SystemPerformanceMonitor
from app.utils.monitoring.transformation_monitor import TransformationMonitor
from datetime import datetime, timedelta
from app.middleware.security import security

bp = Blueprint('system', __name__)


@bp.route('/status', methods=['GET'])
async def get_status():
    """Async status check endpoint"""
    return jsonify({"status": "operational"}), 200


from flask import Blueprint, jsonify
# MODIFICA QUI: Importa system_performance_monitor invece di performance_monitor
from app.utils.monitoring.performance_monitor import system_performance_monitor

system_bp = Blueprint('system', __name__)


@system_bp.route('/metrics', methods=['GET'])
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        # MODIFICA QUI: Usa system_performance_monitor invece di performance_monitor
        metrics = system_performance_monitor.get_metrics()
        return jsonify({'status': 'success', 'metrics': metrics}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@system_bp.route('/backup', methods=['POST'])
async def create_system_backup():
    """Create system backup"""
    try:
        backup_info = backup_manager.create_backup(
            'instance/gold_investment.db',
            metadata={
                'type': 'scheduled',
                'version': '1.0'
            })
        return jsonify({'status': 'success', 'backup': backup_info}), 201
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


system_bp = Blueprint('system', __name__)
system_monitor = SystemPerformanceMonitor()
transformation_monitor = TransformationMonitor()


@system_bp.route('/stats')
@security.require_role('admin')
async def get_system_stats():
    stats = await system_monitor.get_report()
    trans_metrics = transformation_monitor.metriche_trasformazione

    return jsonify({
        'system_status':
        stats['status'],
        'total_transformations':
        trans_metrics['totale'],
        'pending_transformations':
        len([x for x in trans_metrics['stati'].values() if x == 'pending']),
        'completed_today':
        len([
            x for x in trans_metrics['stati'].values()
            if x == 'completed' and x.date() == datetime.now().date()
        ]),
        'system_health': {
            'cpu_usage':
            stats['metriche']['cpu']['percentuale_utilizzo'],
            'memory_usage':
            stats['metriche']['memoria']['utilizzata'],
            'error_rate':
            trans_metrics['fallimenti'] /
            trans_metrics['totale'] if trans_metrics['totale'] > 0 else 0
        }
    })
