
from app import create_app
from app.database import db
from app.models.models import *  # Import all models
from app.utils.optimization import create_indexes

def init_db():
    """Initialize database with proper error handling"""
    try:
        app = create_app()
        with app.app_context():
            # Drop existing tables first
            db.drop_all()
            
            # Create tables
            db.create_all()
            
            # Create indexes
            create_indexes()
            
            print("Database initialized successfully")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db()
