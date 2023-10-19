from typing import Union

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.future import Engine
from sqlalchemy.orm import sessionmaker

from config.config import settings


def create_sessionmaker(bind_engine: Union[AsyncEngine, AsyncConnection, Engine]) -> sessionmaker:
    return sessionmaker(bind=bind_engine, expire_on_commit=False, class_=AsyncSession)


engine = create_async_engine(settings.db.url, echo=True)
async_session = create_sessionmaker(engine)
