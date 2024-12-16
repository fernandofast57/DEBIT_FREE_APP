from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import models
    from app.models import noble_system

    # Inizializza i blueprint
    from app.api.v1 import init_app as init_api
    init_api(app)

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to Gold Investment Platform"})

    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "1.0.0"
        })

    return app