from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

@contextmanager
def atomic_transaction():
    """Ensures all database operations within the context are atomic"""
    try:
        yield
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Transaction failed: {str(e)}")
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in transaction: {str(e)}")
        raise