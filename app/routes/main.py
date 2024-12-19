from flask import Blueprint, send_file
import os

bp = Blueprint('main', __name__)

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