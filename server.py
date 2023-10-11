import datetime
import json

from config.logger import logger

from config.session import async_session
from model import MessageModel

from sqlalchemy.future import select

import asyncio


class Server:
    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()

    async def listen(self):
        pass

    async def handle_echo(self, reader, writer):
        self.reader = reader
        self.writer = writer

        while message_bytes := await self.reader.readline():

            if message_bytes:
                addr = writer.get_extra_info("peername")
                logger.info(f"Входящее подключение с адреса {addr}")

                message_dict = json.loads(message_bytes)
                logger.info(
                    f"Пришло сообщение {message_dict.get('message')} от пользователя "
                    f"{message_dict.get('author_id')}  в чат {message_dict.get('chat_room_id')}"
                )
                message = MessageModel(
                    message=message_dict.get("message"),
                    chat_room_id=message_dict.get("chat_room_id"),
                    author_id=message_dict.get("author_id"),
                )
                async with async_session() as session, session.begin():
                    session.add_all([message])
                    await session.commit()
            else:
                break
            get_message_from = message_dict.get("get_message_from")
            get_message_to = message_dict.get("get_message_to")
            chat_room_id = message_dict.get("chat_room_id")

            message_json, messages_list_obj = await self.messages_for_sent_client(chat_room_id,
                                                                                  get_message_from,
                                                                                  get_message_to)

            logger.info(
                f"Пользователю {message_dict.get('author_id')} отправлено "
                f"{len(messages_list_obj)} сообщений из чата {message_dict.get('chat_room_id')}"
            )

            writer.write(message_json.encode())
            await writer.drain()

        logger.info("Close the connection")
        writer.close()

    async def messages_for_sent_client(self, chat_room_id, get_message_from, get_message_to):
        get_message_from_max_datetime = datetime.datetime.fromtimestamp(
            get_message_to - 60 * 60, tz=datetime.timezone.utc)
        get_message_from_datetime = datetime.datetime.fromtimestamp(
            get_message_from, tz=datetime.timezone.utc)
        get_message_to_datetime = datetime.datetime.fromtimestamp(
            get_message_to, tz=datetime.timezone.utc
        )
        stmt = select(MessageModel).filter(
            MessageModel.chat_room_id == chat_room_id,
            MessageModel.created_at > get_message_from_max_datetime,
            MessageModel.created_at > get_message_from_datetime,
            MessageModel.created_at <= get_message_to_datetime,
        )
        async with async_session() as session, session.begin():
            messages_list = await session.execute(stmt)
        messages_list_obj = []
        for a1 in messages_list.scalars():
            messages_list_obj.append(a1.to_dict)
        message_json = json.dumps(messages_list_obj) + "\n"
        return message_json, messages_list_obj

    async def main(self):
        logger.info("Стартуем сервер")

        server = await asyncio.start_server(
            self.handle_echo, self.host, self.port)

        address = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        print(f"Serving on {address}")

        async with server:
            await server.serve_forever()


async def async_main_server():
    server = Server()
    await server.main()


if __name__ == "__main__":
    asyncio.run(async_main_server())
