from typing import Union

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.config import settings


URL = str(settings.DB_URL)


def create_engine() -> AsyncEngine:
    return create_async_engine(URL)


def create_sessionmaker(bind_engine: Union[AsyncEngine, AsyncConnection]) -> sessionmaker:
    return sessionmaker(
        bind=bind_engine,
        autoflush=False,
        expire_on_commit=False,
        future=True,
        class_=AsyncSession
    )


engine = create_engine()
async_session = create_sessionmaker(engine)

Base = declarative_base(bind=engine)
