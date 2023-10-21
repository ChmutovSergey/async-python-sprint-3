import asyncio
import json
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass

from config.config import settings
from config.logger import logger
from schemas import MassageCreateSchema, MassageGetSchema
from server.chat_handler import ChatRoom
from server.message_handler import Message


@dataclass
class Server:
    host: str = settings.server.host
    port: int = settings.server.port
    number_of_last_available_messages: int = settings.server.count_last_message
    loop = asyncio.new_event_loop()

    async def handle_echo(self, reader: StreamReader, writer: StreamWriter):
        """

        :param reader:
        :param writer:
        :return:
        """
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer

        while message_bytes := await self.reader.read():
            addr = writer.get_extra_info("peername")
            logger.info(f"Incoming connection from address {addr}")

            value_for_create = MassageCreateSchema(**json.loads(message_bytes))
            user_message = value_for_create.message
            author_id = value_for_create.author_id

            message_data = MassageGetSchema(**json.loads(message_bytes))
            chat_room_id = message_data.chat_room_id

            # Check to connect user for chat room
            chat = ChatRoom(user=author_id, chat_room=chat_room_id)
            connect_to_chat_at = await chat.check_connect()

            if connect_to_chat_at:
                # Create message
                message = Message(
                    author=author_id,
                    chat_room=chat_room_id,
                    connect_to_chat_at=connect_to_chat_at,
                    message_data=message_data)
                message_json = await message.send_message(user_message, self.number_of_last_available_messages)

                writer.write(message_json.encode())
            await writer.drain()

        logger.info("Close the connection")
        writer.close()

    async def run_server(self):
        _server = await asyncio.start_server(self.handle_echo, self.host, self.port)
        address = ", ".join(str(sock.getsockname()) for sock in _server.sockets)
        logger.info(f"Сервер запущен на {address}")

        async with _server:
            await _server.serve_forever()


if __name__ == "__main__":
    server = Server()
    asyncio.run(server.run_server())
