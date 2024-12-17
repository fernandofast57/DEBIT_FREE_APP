# app/__init__.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inizializzazione delle estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'ok'})

    # Registrazione dei blueprints
    from app.routes import auth_bp, gold_bp, affiliate_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(gold_bp, url_prefix='/api/gold')
    app.register_blueprint(affiliate_bp, url_prefix='/api/affiliate')

    return app