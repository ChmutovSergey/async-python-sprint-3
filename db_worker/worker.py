from config.logger import logger
from config.session import async_session, engine
from model import Base, MessageModel


class DBWorker:

    @staticmethod
    async def create_message(author_id: int, chat_room_id: int, message: str) -> None:
        logger.info(f"Пришло сообщение {message} от пользователя {author_id} в чат {chat_room_id}")
        message = MessageModel(
            message=message,  # type: ignore
            chat_room_id=chat_room_id,  # type: ignore
            author_id=author_id,  # type: ignore
        )
        async with async_session() as session, session.begin():
            session.add_all([message])
            await session.commit()

    @staticmethod
    async def create_tables() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
