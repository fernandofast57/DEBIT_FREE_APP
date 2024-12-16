
from quart import Quart, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from app.models.models import db
from app.utils.auth import login_manager
from config import Config

migrate = Migrate()

def create_app():
    app = Quart(__name__)
    app.config.from_object(Config)
    
    from app.utils.logging_config import setup_logging
    setup_logging(app)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import models
    from app.models import noble_system

    # Inizializza i blueprint
    from app.api.v1 import init_app as init_api
    init_api(app)

    @app.route("/")
    async def index():
        return jsonify({"message": "Welcome to Gold Investment Platform"})

    @app.route("/health")
    async def health_check():
        return jsonify({
            "status": "healthy",
            "version": "1.0.0"
        })

    return app
