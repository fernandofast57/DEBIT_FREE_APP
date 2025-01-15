# app/utils/database/migrations.py
from flask_migrate import Migrate, upgrade
from alembic import command
from alembic.config import Config
import logging
from typing import Optional
import time
from datetime import datetime

# Configurazione logging avanzato
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('migrations.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


class MigrationManager:

    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.migrate = Migrate(app, db)
        logger.info(f"MigrationManager initialized at {datetime.utcnow()}")

    def init_migrations(self):
        """Inizializza le migrazioni del database"""
        start_time = time.time()
        logger.info("Starting migration initialization...")

        try:
            with self.app.app_context():
                logger.debug("Entering application context")
                upgrade()

            execution_time = time.time() - start_time
            logger.info(
                f"Database migrations initialized successfully in {execution_time:.2f} seconds"
            )
            return True

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Migration initialization failed after {execution_time:.2f} seconds"
            )
            logger.error(f"Error details: {str(e)}")
            logger.exception("Full traceback:")
            return False

    def create_migration(self, message: Optional[str] = None):
        """Crea una nuova migrazione"""
        start_time = time.time()
        logger.info(f"Creating new migration with message: {message}")

        try:
            with self.app.app_context():
                logger.debug("Entering application context")
                config = Config("migrations/alembic.ini")

                logger.debug("Creating revision")
                command.revision(config, message=message, autogenerate=True)

            execution_time = time.time() - start_time
            logger.info(
                f"Migration '{message}' created successfully in {execution_time:.2f} seconds"
            )
            return True

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Migration creation failed after {execution_time:.2f} seconds"
            )
            logger.error(f"Error details: {str(e)}")
            logger.exception("Full traceback:")
            return False

    def apply_migrations(self):
        """Applica le migrazioni pendenti"""
        start_time = time.time()
        logger.info("Starting to apply migrations...")

        try:
            with self.app.app_context():
                logger.debug("Entering application context")

                # Log dello stato del database prima della migrazione
                logger.info("Current database state before migration:")
                with self.db.engine.connect() as conn:
                    tables = self.db.inspect(self.db.engine).get_table_names()
                    logger.info(f"Existing tables: {', '.join(tables)}")

                upgrade()

                # Log dello stato del database dopo la migrazione
                logger.info("Database state after migration:")
                with self.db.engine.connect() as conn:
                    tables = self.db.inspect(self.db.engine).get_table_names()
                    logger.info(f"Updated tables: {', '.join(tables)}")

            execution_time = time.time() - start_time
            logger.info(
                f"Migrations applied successfully in {execution_time:.2f} seconds"
            )
            return True

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Migration application failed after {execution_time:.2f} seconds"
            )
            logger.error(f"Error details: {str(e)}")
            logger.exception("Full traceback:")
            return False
