
from app import create_app
from app.database import db
from app.models.models import *
from app.utils.optimization import create_indexes
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database with proper error handling and logging"""
    try:
        app = create_app()
        with app.app_context():
            logger.info("Starting database initialization...")
            
            logger.info("Dropping existing tables...")
            db.drop_all()

            logger.info("Creating new tables...")
            db.create_all()

            logger.info("Creating indexes for optimization...")
            create_indexes()

            logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Critical error during database initialization: {str(e)}")
        raise

if __name__ == "__main__":
    init_db()
