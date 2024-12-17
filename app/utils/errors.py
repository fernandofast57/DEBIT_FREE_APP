# app/utils/errors.py

from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Registra gli handler per gli errori dell'applicazione."""

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handler generico per errori HTTP."""
        response = jsonify({
            'error': {
                'code': error.code,
                'name': error.name,
                'description': error.description
            }
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handler per errori generici non HTTP."""
        app.logger.error(f'Errore non gestito: {str(error)}', exc_info=True)
        response = jsonify({
            'error': {
                'code': 500,
                'name': 'Internal Server Error',
                'description': f'Si è verificato un errore: {str(error)}',
                'details': error.__class__.__name__
            }
        })
        response.status_code = 500
        return response

    # Custom error handlers specifici per la nostra applicazione
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handler per errori di Bad Request."""
        response = jsonify({
            'error': {
                'code': 400,
                'name': 'Bad Request',
                'description': str(error.description)
            }
        })
        response.status_code = 400
        return response

    return app
