from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

Base = declarative_base()


class DatabaseManager:

    def __init__(self, db_url: str):
        self.sync_engine = create_engine(db_url, echo=True, pool_pre_ping=True)

        self.async_engine = create_async_engine(
            f"sqlite+aiosqlite://{db_url.split('sqlite://')[-1]}",
            echo=True,
            pool_pre_ping=True)

        # Sync session maker
        self.SessionLocal = sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.sync_engine)

        # Async session maker
        self.AsyncSessionLocal = sessionmaker(class_=AsyncSession,
                                              autocommit=False,
                                              autoflush=False,
                                              bind=self.async_engine,
                                              expire_on_commit=False)

    @asynccontextmanager
    async def get_async_session(self):
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def get_sync_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def create_all(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# Istanza globale del database manager
db = DatabaseManager("sqlite:///instance/gold_investment.db")
