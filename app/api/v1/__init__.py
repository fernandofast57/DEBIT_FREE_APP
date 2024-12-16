from app.api.v1.transfers import bp as transfers_bp
from app.api.v1.transformations import bp as transformations_bp
from app.api.v1.bonuses import bp as bonuses_bp

def init_app(app):
    app.register_blueprint(transfers_bp)
    app.register_blueprint(transformations_bp)
    app.register_blueprint(bonuses_bp)