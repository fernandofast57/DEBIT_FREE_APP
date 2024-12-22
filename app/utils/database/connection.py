
from typing import Optional
from contextlib import contextmanager
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from app.utils.logging_config import logger

class DatabaseManager:
    def __init__(self, db_url: str, pool_size: int = 10):
        self.engine = sqlalchemy.create_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800
        )
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError

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
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

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
            self.logger.error(f"Failed to create database engine: {str(e)}")
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
            self.logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    def check_connection(self) -> bool:
        """Verifica la connessione al database"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except OperationalError as e:
            self.logger.error(f"Database connection check failed: {str(e)}")
            return False
