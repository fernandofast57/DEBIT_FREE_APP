from flask import Blueprint, send_file, jsonify
import os

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    """Root endpoint that returns API status"""
    return jsonify({
        "status": "online",
        "service": "Gold Investment API",
        "version": "1.0"
    }), 200

@bp.route('/download/project-doc', methods=['GET'])
def download_project_doc():
    """Download the project documentation file"""
    try:
        return send_file('MASTER_PROJECT.md',
                        mimetype='text/markdown',
                        as_attachment=True,
                        download_name='GOLD_INVESTMENT_PROJECT.md')
    except Exception as e:
        return str(e), 400