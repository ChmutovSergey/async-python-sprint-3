from typing import Generator

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from config.config import settings


engine = create_async_engine(settings.DB_URL)

SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
