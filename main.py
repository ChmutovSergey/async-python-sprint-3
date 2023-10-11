from sqlalchemy.orm import selectinload

from config.logger import logger
from config.session import async_session
from model import UserModel, ChatRoomModel, MessageModel

from sqlalchemy.future import select

import asyncio

from server import Server


async def async_main_server():
    await init_data()

    server = Server()

    await server.main()


async def init_data():
    async with async_session() as session, session.begin():
        stmt = select(UserModel).options(selectinload(UserModel.messages))

        user_list = await session.execute(stmt)
        users_list_obj = []

        for a1 in user_list.scalars():
            users_list_obj.append(a1)

        logger.info(f"user {len(users_list_obj)}")

        stmt = select(ChatRoomModel).options(selectinload(ChatRoomModel.messages))
        chat_room_list = await session.execute(stmt)
        chat_room_list_obj = []

        for a1 in chat_room_list.scalars():
            chat_room_list_obj.append(a1)

        logger.info(f"chat_rooms {len(chat_room_list_obj)}")

        stmt = select(MessageModel)
        messages_list = await session.execute(stmt)
        messages_list_obj = []

        for a1 in messages_list.scalars():
            messages_list_obj.append(a1)

        logger.info(f"messages {len(messages_list_obj)}")

        await session.commit()


asyncio.run(async_main_server())
