from dataclasses import dataclass

from sqlalchemy.future import select

from config.session import async_session
from model import PeerModel


@dataclass
class ChatRoom:
    user: int
    chat_room: int

    async def check_connect(self) -> float | None:
        stmt = select(PeerModel).filter(
            PeerModel.chat_room_id == self.chat_room,
            PeerModel.user_id == self.user,
        )
        async with async_session() as session, session.begin():
            link_user_chat_list = await session.execute(stmt)

        link_user_chat_list_obj = []
        for a1 in link_user_chat_list.scalars():
            link_user_chat_list_obj.append(a1)

        if link_user_chat_list_obj:
            return link_user_chat_list_obj[0].created_at

        return None
