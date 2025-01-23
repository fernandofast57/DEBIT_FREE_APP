
from typing import Optional, Type, TypeVar, List
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from flask_sqlalchemy import SQLAlchemy
import logging
from typing import Generator

T = TypeVar('T')
db = SQLAlchemy()

class DatabaseManager:
    def __init__(self, db_url: str):
        self.logger = logging.getLogger(__name__)
        self._setup_engines(db_url)
        self._setup_logging()

    def _setup_logging(self):
        handler = logging.FileHandler('logs/database.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _setup_engines(self, db_url: str) -> None:
        engine_config = {
            'echo': True,
            'pool_pre_ping': True,
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800
        }
        
        self.sync_engine = create_engine(db_url, **engine_config)
        self.async_engine = create_async_engine(
            f"sqlite+aiosqlite://{db_url.split('sqlite://')[-1]}", 
            **engine_config
        )
        
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.sync_engine
            )
        )
        
        self.AsyncSessionLocal = sessionmaker(
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            bind=self.async_engine,
            expire_on_commit=False
        )

    async def create_all(self) -> None:
        """Create all database tables"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(db.Model.metadata.create_all)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create database tables: {str(e)}")
            raise

    async def drop_all(self) -> None:
        """Drop all database tables"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(db.Model.metadata.drop_all)
            self.logger.info("Database tables dropped successfully")
        except Exception as e:
            self.logger.error(f"Failed to drop database tables: {str(e)}")
            raise

    @asynccontextmanager
    async def get_async_session(self) -> Generator[AsyncSession, None, None]:
        """Get async database session"""
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()

    @contextmanager
    def get_sync_session(self) -> Generator[scoped_session, None, None]:
        """Get sync database session"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    async def check_connection(self) -> bool:
        """Check database connection"""
        try:
            async with self.get_async_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            self.logger.error(f"Connection check failed: {str(e)}")
            return False

    # Generic CRUD operations
    async def create(self, model: Type[T], **kwargs) -> T:
        """Create a new record"""
        async with self.get_async_session() as session:
            obj = model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def get(self, model: Type[T], id: int) -> Optional[T]:
        """Get a record by id"""
        async with self.get_async_session() as session:
            return await session.get(model, id)

    async def get_all(self, model: Type[T]) -> List[T]:
        """Get all records"""
        async with self.get_async_session() as session:
            result = await session.execute(text(f"SELECT * FROM {model.__tablename__}"))
            return result.scalars().all()

    async def update(self, model: Type[T], id: int, **kwargs) -> Optional[T]:
        """Update a record"""
        async with self.get_async_session() as session:
            obj = await session.get(model, id)
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                await session.commit()
                await session.refresh(obj)
            return obj

    async def delete(self, model: Type[T], id: int) -> bool:
        """Delete a record"""
        async with self.get_async_session() as session:
            obj = await session.get(model, id)
            if obj:
                await session.delete(obj)
                await session.commit()
                return True
            return False

# Initialize database manager with SQLite
db_manager = DatabaseManager("sqlite:///instance/gold_investment.db")
