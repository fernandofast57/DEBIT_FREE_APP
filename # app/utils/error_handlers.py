# app/utils/error_handlers.py
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException
from app.database import db


def register_error_handlers(app):
    """Registra gli handler per gli errori dell'applicazione"""

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.info(f'Page not found: {request.url}')
        if request.is_json:
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {str(error)}')
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Forbidden access: {request.url}')
        if request.is_json:
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Gestisce tutte le altre eccezioni"""

        # Registra l'errore nel log
        app.logger.error(f'Unhandled Exception: {str(error)}', exc_info=True)

        # Se è un errore HTTP, usa il suo codice di stato
        if isinstance(error, HTTPException):
            status_code = error.code
            message = error.description
        else:
            status_code = 500
            message = 'An unexpected error occurred'

        # Rollback della sessione del database in caso di errore
        try:
            db.session.rollback()
        except Exception as e:
            app.logger.error(f'Error during database rollback: {str(e)}')

        # Restituisci JSON per le richieste API
        if request.is_json:
            return jsonify({
                'error': message,
                'status_code': status_code
            }), status_code

        # Altrimenti renderizza un template HTML
        return render_template('errors/generic.html',
                               error_code=status_code,
                               message=message), status_code
