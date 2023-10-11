from typing import Generator

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from config.config import settings


engine = create_async_engine(settings.DB_URL, echo=True)

async_session = AsyncSession(engine, expire_on_commit=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    engine.dispose()
    async with engine.begin() as conn:
        yield conn
        conn.close()
