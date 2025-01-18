from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create database instance
db = SQLAlchemy()

# Create engine and session
engine = create_engine('sqlite:///:memory:', echo=True)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Create declarative base
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize the database"""
    import app.models.models  # Import all models
    Base.metadata.create_all(bind=engine)


def shutdown_session(exception=None):
    """Remove database session at request end"""
    db_session.remove()
