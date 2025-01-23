from typing import Optional
from contextlib import contextmanager
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.utils.logging_config import logger

class DatabaseManager:
    """Gestore connessioni database con retry e pool"""

    def __init__(self, uri: str, pool_size: int = 5, max_overflow: int = 10):
        self.uri = uri
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.logger = logging.getLogger('database')
        self._setup_logging()
        self.engine = self._create_engine()
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def _setup_logging(self):
        handler = logging.FileHandler('logs/database.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG) # Increased logging level for more granular detail

    def _create_engine(self):
        """Crea engine SQLAlchemy con configurazione ottimizzata"""
        try:
            return create_engine(
                self.uri,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True
            )
        except SQLAlchemyError as e:
            self.logger.exception(f"Failed to create database engine: {str(e)}") # Use exception for traceback
            raise

    @contextmanager
    def session_scope(self):
        """Context manager per gestire le sessioni del database"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.exception(f"Database session error: {str(e)}") # Use exception for traceback
            raise
        finally:
            session.close()

    def check_connection(self) -> bool:
        """Verifica la connessione al database"""
        try:
            with self.session_scope() as session:
                session.execute("SELECT 1")
                return True
        except OperationalError as e:
            self.logger.exception(f"Database connection check failed: {str(e)}") # Use exception for traceback
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error: {str(e)}") # Use exception for traceback
            return False