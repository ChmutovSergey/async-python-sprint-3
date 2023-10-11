import asyncio
import json

from config.logger import logger
from config.session import async_session
from model import MessageModel


class Server:
    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
        pass

    async def listen(self):
        pass

    async def reliable_receive(self) -> bytes:
        """
        Функция приёма данных
        Обратите внимание, что возвращает тип bytes
        """
        b = b''
        while True:
            part_len = int.from_bytes(await self.reader.readexactly(2),
                                      "big")  # Определяем длину ожидаемого куска
            if part_len == 0:  # Если пришёл кусок нулевой длины, то приём окончен
                return b
            b += await self.reader.readexactly(part_len)  # Считываем сам кусок

    async def handle_echo(self, reader, writer):
        self.reader = reader
        self.writer = writer

        while True:
            f = self.loop.run_until_complete(self.reliable_receive())
            print(f)

            addr = writer.get_extra_info('peername')
            print(addr)

            await writer.drain()

        print("Close the connection")
        writer.close()

    async def main(self):
        logger.info("Стартуем сервер")

        server = await asyncio.start_server(
            self.handle_echo, self.host, self.port)

        address = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        print(f"Serving on {address}")

        async with server:
            await server.serve_forever()
