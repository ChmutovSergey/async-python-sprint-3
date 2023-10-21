import asyncio
import datetime
import json
import secrets
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from chat_handler import ChatRoom
from config.config import settings
from config.logger import logger
from config.session import async_session
from db_worker.worker import DBWorker
from model import UserModel


@dataclass
class Client:
    user_id: UUID
    chat_room_id: UUID
    server_host: str = settings.client.host
    server_port: int = settings.client.port
    get_messages_in_time: int = 5 * 60
    get_message_from: float = datetime.datetime.now(tz=datetime.timezone.utc).timestamp() - get_messages_in_time
    get_message_to: float = 0.0

    async def connect(self):
        for i in range(1000):
            logger.info("Open the connection")
            reader, writer = await asyncio.open_connection(self.server_host, self.server_port)
            message: str = f"Сообщение {i} от {self.user_id}"

            await self.send(reader, writer, message)
            writer.close()

        logger.info("Close the connection")

    async def send(self, reader, writer, message: str):
        self.get_message_to = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        message = json.dumps(
            {
                "message": message,
                "chat_room_id": self.chat_room_id,
                "author_id": self.user_id,
                "get_message_from": self.get_message_from,
                "get_message_to": self.get_message_to,
            }
        )
        writer.write(message.encode())
        writer.write_eof()
        self.datetime_last_request = datetime.datetime.now()
        await writer.drain()
        logger.info(f"Message sent for chat {self.chat_room_id}")
        data = await reader.readline()
        logger.info(f"Arrived messages {data} for chat {self.chat_room_id}")

        logger.info("Close the connection")
        writer.close()
        self.get_message_from = self.get_message_to


@dataclass
class Launcher:
    chat_room: ChatRoom = ChatRoom()

    @staticmethod
    async def get_users():
        async with async_session() as session, session.begin():
            stmt = select(UserModel).options(selectinload(UserModel.messages))

            user_list = await session.execute(stmt)
            users_list_obj = []

            for a1 in user_list.scalars():
                users_list_obj.append(a1)

            if not users_list_obj:
                for i in range(5):
                    users_list_obj.append(UserModel(name=f"user_{i}", ))
                session.add_all(users_list_obj)

            return users_list_obj

    async def run(self):
        users = await self.get_users()
        chats = await self.chat_room.get_chats()

        user = secrets.choice(users)
        chat = secrets.choice(chats)

        await self.chat_room.connect_to_chat(user.id, chat.id)
        logger.info(f"Запуск клиента пользователя {user.name} для чата {chat.name}")
        client = Client(user_id=user.id, chat_room_id=chat.id)

        await client.connect()


if __name__ == "__main__":
    db_worker = DBWorker()
    asyncio.run(db_worker.create_tables())

    launcher = Launcher()
    asyncio.run(launcher.run())
