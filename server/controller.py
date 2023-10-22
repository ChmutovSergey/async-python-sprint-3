from dataclasses import dataclass

from sqlalchemy.future import select

from config.session import async_session
from model import ChatRoomModel, CommentModel, PeerModel, MessageModel, UserModel, Base
from schemas import CommentCreateSchema, PeerCreateSchema, MassageCreateSchema, MassageGetSchema, BaseModel
from server.chat_handler import ChatRoom
from server.message_handler import Message


@dataclass
class BaseController:
    model: Base

    async def get_data_by_id(self, _id):
        async with async_session() as session, session.begin():
            stmt = select(self.model)
            if _id is not None:
                stmt = stmt.filter(self.model.id == _id)
        return await session.execute(stmt)


@dataclass
class BaseCreateController(BaseController):
    schema_create: BaseModel

    async def commit_data(self, body):
        value = self.schema_create(**body)
        async with async_session() as session, session.begin():
            session.add(self.model(**value.__dict__))
            await session.commit()


@dataclass
class PostNameMixin:
    model: Base

    async def post_data_by_name(self, name):
        data = self.model(name=name)
        async with async_session() as session, session.begin():
            session.add(data)
            await session.commit()


@dataclass
class UserModelController(BaseController, PostNameMixin):
    model: UserModel = UserModel


@dataclass
class ChatRoomController(BaseController, PostNameMixin):
    model: ChatRoomModel = ChatRoomModel


@dataclass
class PeerController(BaseCreateController):
    model: PeerModel = PeerModel
    schema_create: PeerCreateSchema = PeerCreateSchema

    async def get_chat_room_by_user_id(self, _id: int | None):
        async with async_session() as session, session.begin():
            stmt = select(self.model)
            if _id is not None:
                stmt = stmt.filter(self.model.user_id == _id)
        return await session.execute(stmt)


@dataclass
class MessageController(BaseCreateController):
    model: MessageModel = MessageModel
    schema_get: MassageGetSchema = MassageGetSchema
    schema_create: MassageCreateSchema = MassageCreateSchema

    async def __get_message_data(self, body):
        return self.schema_get(**body)

    async def send_message(self, body):
        value = await self.__get_message_data(body)
        chat = ChatRoom(user=value.author_id, chat_room=value.chat_room_id)
        connect_to_chat_at = await chat.check_connect()

        if connect_to_chat_at:
            message = Message(
                author=value.author_id,
                chat_room=value.chat_room_id,
                connect_to_chat_at=connect_to_chat_at,
                message_data=value)
            return await message.sent_message_for_client()


@dataclass
class CommentController(BaseCreateController):
    model: CommentModel = CommentModel
    schema_create: CommentCreateSchema = CommentCreateSchema

    async def get_chat_room_by_user_id(self, _id: int | None):
        async with async_session() as session, session.begin():
            stmt = select(self.model)
            if _id is not None:
                stmt = stmt.filter(self.model.message_id == _id)
        return await session.execute(stmt)
