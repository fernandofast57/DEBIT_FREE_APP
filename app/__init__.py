
from quart import Quart
from app.models.models import db
from app.utils.errors import register_error_handlers

def create_app():
    app = Quart(__name__)
    
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': True,
        'PROVIDE_AUTOMATIC_OPTIONS': True
    })

    db.init_app(app)
    register_error_handlers(app)

    from app.api.v1.transformations import bp as transformations_bp
    app.register_blueprint(transformations_bp)

    return app
