
from flask_migrate import Migrate, upgrade
from alembic import command
from alembic.config import Config
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.migrate = Migrate(app, db)
        
    def init_migrations(self):
        try:
            with self.app.app_context():
                upgrade()
            logger.info("Database migrations initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize migrations: {str(e)}")
            return False
            
    def create_migration(self, message: Optional[str] = None):
        try:
            with self.app.app_context():
                config = Config("migrations/alembic.ini")
                command.revision(config, message=message, autogenerate=True)
            logger.info(f"Migration created successfully: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to create migration: {str(e)}")
            return False
            
    def apply_migrations(self):
        try:
            with self.app.app_context():
                upgrade()
            logger.info("Migrations applied successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to apply migrations: {str(e)}")
            return False

migration_manager = MigrationManager(None, None)
