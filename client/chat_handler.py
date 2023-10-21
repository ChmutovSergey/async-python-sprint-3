from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from config.session import async_session
from model import ChatRoomModel, ConnectedChatRoomModel


class ChatRoom:

    @staticmethod
    async def get_chats() -> list:
        async with async_session() as session, session.begin():
            stmt = select(ChatRoomModel).options(selectinload(ChatRoomModel.messages))

            chat_room_list = await session.execute(stmt)
            chat_room_list_obj = []

            for a1 in chat_room_list.scalars():
                chat_room_list_obj.append(a1)

            if not chat_room_list_obj:
                for i in range(2):
                    chat_room_list_obj.append(ChatRoomModel(name=f"chat_room_name{i}", ))
                session.add_all(chat_room_list_obj)

            return chat_room_list_obj

    @staticmethod
    async def connect_to_chat(user_id, chat_room_id) -> list:
        async with async_session() as session, session.begin():
            stmt = select(ConnectedChatRoomModel).filter(
                ConnectedChatRoomModel.chat_room_id == chat_room_id,
                ConnectedChatRoomModel.user_id == user_id,
            )

            connect_chat_room_list = await session.execute(stmt)

            connect_chat_room_list_obj = []
            for a1 in connect_chat_room_list.scalars():
                connect_chat_room_list_obj.append(a1)

            if not connect_chat_room_list_obj:
                connect_chat_room_list_obj.append(
                    ConnectedChatRoomModel(
                        user_id=user_id,
                        chat_room_id=chat_room_id,
                    )
                )

                session.add_all(connect_chat_room_list_obj)

            return connect_chat_room_list_obj
