import asyncio
from model import TariffOrderModel

from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/async_python_sprint_3"


async def async_main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        async with session.begin():
            tariffs = []
            for i in range(5):
                tariffs.append(
                    TariffOrderModel(type=f"type{i}", tariff_concat_code=f"tariff_concat_code{i}")
                )

            session.add_all(tariffs)
            stmt = select(TariffOrderModel)
            result = await session.execute(stmt)

            for a1 in result.scalars():
                print(a1)

            result = await session.execute(select(TariffOrderModel).order_by(TariffOrderModel.id))

            a1 = result.scalars().first()
            print(a1.type)

            a1.type = "new data"
            print(a1.type)

            await session.commit()
            print(a1.type)

    await engine.dispose()


asyncio.run(async_main())
