from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager, contextmanager
import logging
from typing import Generator
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

#The rest of the original file is removed because it is replaced with the new db management system.