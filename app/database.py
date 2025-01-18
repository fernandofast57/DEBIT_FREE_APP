
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager, contextmanager
import logging
from typing import Generator

Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_url: str):
        self.logger = logging.getLogger(__name__)
        self._setup_engines(db_url)
        
    def _setup_engines(self, db_url: str) -> None:
        engine_config = {
            'echo': True,
            'pool_pre_ping': True,
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30
        }
        
        self.sync_engine = create_engine(db_url, **engine_config)
        self.async_engine = create_async_engine(
            f"sqlite+aiosqlite://{db_url.split('sqlite://')[-1]}", 
            **engine_config
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.sync_engine
        )
        
        self.AsyncSessionLocal = sessionmaker(
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            bind=self.async_engine,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_async_session(self) -> Generator[AsyncSession, None, None]:
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()

    @contextmanager
    def get_sync_session(self) -> Generator[AsyncSession, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    async def create_all(self) -> None:
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def check_connection(self) -> bool:
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            self.logger.error(f"Connection check failed: {str(e)}")
            return False

db = DatabaseManager("sqlite:///instance/gold_investment.db")
