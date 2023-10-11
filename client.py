import asyncio
import json


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

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.server_host, self.server_port)

        # while True:
        for i in range(100):
            await self.send(self.reader, self.writer, i)

        print("Close the connection")
        self.writer.close()

    async def send(self, reader, writer, i):
        message = json.dumps(
            {
                "message": f"Сообщение {i} от {self.user_id}",
                "chat_room_id": self.chat_room_id,
                "author_id": self.user_id,
            }
        ).encode()
        self.reliable_send(data=message)

        await asyncio.sleep(5)
        await self.writer.drain()

    def reliable_send(self, data: bytes) -> None:
        """
        Функция отправки данных в сокет
        Обратите внимание, что данные ожидаются сразу типа bytes
        """
        # Разбиваем передаваемые данные на куски максимальной длины 0xffff (65535)
        for chunk in (data[_:_ + 0x1f] for _ in range(0, len(data), 0x1f)):
            self.writer.write(len(chunk).to_bytes(2, "big"))
            self.writer.write(chunk)

        self.writer.write(len("").to_bytes(2, "big"))


async def tcp_echo_client1(message):
    message = f"{message} Клиент 1"
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", 8888)

    while True:
        await asyncio.sleep(5)
        print(f"Send: {message!r}")
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        print(f"Received: {data.decode()!r}")

    print("Close the connection")
    writer.close()

client = Client(
    user_id="81c95c92-8a18-4b22-8ffe-b4163443162f",
    chat_room_id="9b8466d0-df95-4ec9-b9a3-b011577bf046"
)

asyncio.run(client.connect())
