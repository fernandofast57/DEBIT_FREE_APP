from flask import Flask, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config.settings import Config
from app.utils.monitoring.performance_monitor import PerformanceMonitor

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.api.v1.index import api_v1
    app.register_blueprint(api_v1)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app

# Configurazione per l'esecuzione diretta
if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        use_reloader=False,
        threaded=True
    )