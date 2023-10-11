from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from config.config import settings


engine = create_async_engine(settings.DB_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> Generator[Session, None, None]:
    async with async_session() as session, session.begin():
        yield session
