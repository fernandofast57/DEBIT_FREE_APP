from flask import Flask, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager  # <-- IMPORTAZIONE LoginManager
from app.config.settings import Config
import asyncio
from app.utils.monitoring.monitoring_setup import setup_monitoring
from app.utils.cache.redis_manager import cache_manager

# Initialize cache manager
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(cache_manager.initialize())

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()  # <-- INIZIALIZZAZIONE LoginManager
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from app.models.models import User
    return User.query.get(int(user_id))


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    setup_monitoring(app)
    login_manager.init_app(app)  # <-- INIZIALIZZAZIONE LoginManager

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
    app.run(host='0.0.0.0',
            port=8080,
            debug=False,
            use_reloader=False,
            threaded=True)
