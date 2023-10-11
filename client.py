import datetime
import json

from sqlalchemy.orm import selectinload

from model import UserModel, ChatRoomModel

from sqlalchemy.future import select

import asyncio

from config.session import async_session


class Client:
    def __init__(
            self,
            user_id,
            chat_room_id,
            server_host="127.0.0.1",
            server_port=8888
    ):
        self.user_id = user_id
        self.chat_room_id = chat_room_id
        self.server_host = server_host
        self.server_port = server_port
        self.get_message_from = datetime.datetime.now(
            tz=datetime.timezone.utc).timestamp() - 20 * 60
        self.get_message_to = 0

    async def connect(self):
        for i in range(20):
            reader, writer = await asyncio.open_connection(self.server_host, self.server_port)
            await self.send(reader, writer, 1)
            writer.close()

        print("Close the connection")

    async def send(self, reader, writer, i):
        self.get_message_to = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        message = json.dumps(
            {
                "message": f"Сообщение {i} от {self.user_id}",
                "chat_room_id": self.chat_room_id,
                "author_id": self.user_id,
                "get_message_from": self.get_message_from,
                "get_message_to": self.get_message_to,
            }
        ) + "\n"
        print(message)

        self.writer.write(message.encode())
        self.datetime_last_request = datetime.datetime.now()
        await writer.drain()

        data = await reader.readline()
        print(f"Received: {data.decode()!r}")

        print("Close the connection")
        writer.close()
        self.get_message_from = self.get_message_to

        await asyncio.sleep(5)


async def client_main():
    async with async_session() as session, session.begin():
        stmt = select(UserModel).options(selectinload(UserModel.messages))

        user_list = await session.execute(stmt)
        users_list_obj = []
        for a1 in user_list.scalars():
            users_list_obj.append(a1)

        stmt = select(ChatRoomModel).options(selectinload(ChatRoomModel.messages))

        chat_room_list = await session.execute(stmt)
        chat_room_list_obj = []

        for a1 in chat_room_list.scalars():
            chat_room_list_obj.append(a1)

    client = Client(
        user_id=str(users_list_obj[0].id),
        chat_room_id=str(chat_room_list_obj[1].id),
    )

    await client.connect()

asyncio.run(client_main())
