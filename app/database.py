from typing import Generator, Optional, Type, TypeVar, List
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text
import logging

Base = declarative_base()
T = TypeVar('T')

class DatabaseManager:
    def __init__(self, database_url: str):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    def _setup_logging(self):
        handler = logging.FileHandler('logs/database.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)


    @asynccontextmanager
    async def get_async_session(self) -> Generator[AsyncSession, None, None]:
        session = self.async_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()

    async def create_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def check_connection(self) -> bool:
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
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

db = DatabaseManager("sqlite+aiosqlite:///instance/gold_investment.db")