import datetime
import json
from dataclasses import dataclass

from sqlalchemy.future import select

from config.logger import logger
from config.session import async_session
from db_worker.worker import DBWorker
from model import MessageModel
from schemas import MassageGetSchema


@dataclass
class Message:
    author: int
    chat_room: int
    connect_to_chat_at: float
    message_data: MassageGetSchema
    db_worker: DBWorker = DBWorker()

    async def save_message(self, user_message: str):
        await self.db_worker.create_message(self.author, self.chat_room, user_message)

    async def sent_message_for_client(self, number_of_last_available_messages: int = 10) -> str:
        if (get_message_from := self.message_data.get_message_from) is None:
            get_message_from = 0
        if (get_message_to := self.message_data.get_message_to) is None:
            get_message_to = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

        get_message_from_max_datetime = (
            datetime.datetime.fromtimestamp(get_message_to - 60 * 60, tz=datetime.timezone.utc))
        get_message_from_datetime = datetime.datetime.fromtimestamp(get_message_from, tz=datetime.timezone.utc)
        get_message_to_datetime = datetime.datetime.fromtimestamp(get_message_to, tz=datetime.timezone.utc)

        stmt = select(MessageModel).filter(
            MessageModel.chat_room_id == self.chat_room,
            MessageModel.created_at > self.connect_to_chat_at,
            MessageModel.created_at > get_message_from_max_datetime,
            MessageModel.created_at > get_message_from_datetime,
            MessageModel.created_at <= get_message_to_datetime,
        ).order_by(MessageModel.created_at.desc()).limit(number_of_last_available_messages)

        async with async_session() as session, session.begin():
            messages_list = await session.execute(stmt)
        messages_list_obj = []

        for a1 in messages_list.scalars():
            messages_list_obj.append(a1.to_dict)
        message_json = json.dumps(messages_list_obj) + "\n"

        logger.info(
            f"Пользователю {self.author} отправлено {len(messages_list_obj)} сообщений из чата {self.chat_room}"
        )

        return message_json

    async def send_message(self, user_message: str, number_of_last_available_messages: int) -> str:
        # Save user message
        await self.save_message(user_message)
        message_json = await self.sent_message_for_client(number_of_last_available_messages)

        return message_json
