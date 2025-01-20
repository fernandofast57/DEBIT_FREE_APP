
from app import create_app
from app.database import db
from app.models.models import *  # Import all models
from app.utils.optimization import create_indexes

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        create_indexes()  # Create indexes after tables
        print("Database initialized successfully")

if __name__ == "__main__":
    init_db()
