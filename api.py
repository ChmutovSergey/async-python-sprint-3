import asyncio
import datetime
import json

import pydantic
from aiohttp import web
from sqlalchemy.future import select

from config.config import settings
from config.session import async_session, engine
from model import ChatRoomModel, CommentModel, ConnectedChatRoomModel, MessageModel, UserModel, Base
from schemas import CommentCreateSchema, ConnectedChatRoomSchema, MassageCreateSchema, MassageGetSchema
from server import Server


class UserHandle:

    @staticmethod
    async def get(request):
        async with async_session() as session, session.begin():
            stmt = select(UserModel)
            if user_id := request.match_info.get("user_id"):
                stmt = stmt.filter(UserModel.id == user_id)
            user_list = await session.execute(stmt)
            users_list_obj = []
            for a1 in user_list.scalars():
                users_list_obj.append(a1.to_dict)
            users_json = json.dumps(users_list_obj)
        return web.json_response(body=users_json.encode())

    @staticmethod
    async def post(request):
        body = await request.json()
        if name := body.get("name"):
            user = UserModel(name=name)
            async with async_session() as session, session.begin():
                session.add(user)
                await session.commit()
            return web.json_response(status=201)
        return web.json_response(status=400)


class ChatRoomHandle:
    @staticmethod
    async def get(request):
        async with async_session() as session, session.begin():
            stmt = select(ChatRoomModel)
            if chat_room_id := request.match_info.get("chat_room_id"):
                stmt = stmt.filter(ChatRoomModel.id == chat_room_id)
            chat_rooms_list = await session.execute(stmt)
            chat_rooms_list_obj = []
            for a1 in chat_rooms_list.scalars():
                chat_rooms_list_obj.append(a1.to_dict)
            chat_rooms_json = json.dumps(chat_rooms_list_obj)
        return web.json_response(body=chat_rooms_json.encode())

    @staticmethod
    async def post(request):
        body = await request.json()
        if name := body.get("name"):
            chat_room = ChatRoomModel(name=name)
            async with async_session() as session, session.begin():
                session.add(chat_room)
                await session.commit()
            return web.json_response(status=201)
        return web.json_response(status=400)


class ConnectHandle:
    @staticmethod
    async def get(request):
        user_id = request.match_info.get("user_id")
        async with async_session() as session, session.begin():
            stmt = select(ConnectedChatRoomModel).filter(
                ConnectedChatRoomModel.user_id == user_id,
            )
            chat_rooms_list = await session.execute(stmt)
            chat_rooms_list_obj = []
            for a1 in chat_rooms_list.scalars():
                chat_rooms_list_obj.append(a1.to_dict)
            chat_rooms_json = json.dumps(chat_rooms_list_obj)
        return web.json_response(body=chat_rooms_json.encode())

    @staticmethod
    async def post(request):
        body = await request.json()
        try:
            value = ConnectedChatRoomSchema(**body)
            async with async_session() as session, session.begin():
                session.add(ConnectedChatRoomModel(**value.__dict__))
                await session.commit()
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())
        else:
            return web.json_response(status=201)


class MessageHandle:

    @staticmethod
    async def get(request):
        body = await request.json()
        try:
            value = MassageGetSchema(**body)
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())

        if (get_message_from := value.get_message_from) is None:
            get_message_from = 0
        if (get_message_to := value.get_message_to) is None:
            get_message_to = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

        server = Server()

        connect_to_chat_at = await server.check_connect_to_chat_room(
            user_id=value.author_id,
            chat_room_id=value.chat_room_id
        )

        if connect_to_chat_at:
            message_json, _ = await server.messages_for_sent_client(
                chat_room_id=value.chat_room_id,
                get_message_from=float(get_message_from),
                get_message_to=float(get_message_to),
                connect_to_chat_at=connect_to_chat_at
            )

            return web.json_response(body=message_json.encode())

    @staticmethod
    async def post(request):
        body = await request.json()
        try:
            message = MassageCreateSchema(**body)
            async with async_session() as session, session.begin():
                session.add(MessageModel(**message.__dict__))
                await session.commit()
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())
        finally:
            return web.json_response(status=201)


class CommentHandle:

    @staticmethod
    async def get(request):
        async with async_session() as session, session.begin():
            stmt = select(CommentModel)
            if message_id := request.match_info.get("message_id"):
                stmt = stmt.filter(CommentModel.message_id == message_id)
            comment_list = await session.execute(stmt)
            comment_list_obj = []
            for a1 in comment_list.scalars():
                comment_list_obj.append(a1.to_dict)
            comments_json = json.dumps(comment_list_obj)
        return web.json_response(body=comments_json.encode())

    @staticmethod
    async def post(request):
        body = await request.json()
        try:
            comment = CommentCreateSchema(**body)
            async with async_session() as session, session.begin():
                session.add(CommentModel(**comment.__dict__))
                await session.commit()
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())
        finally:
            return web.json_response(status=201)


app = web.Application()
app.add_routes(
    [
        web.get("/users/", UserHandle.get),
        web.get("/users/{user_id}", UserHandle.get),
        web.post("/user/", UserHandle.post),
        web.get("/chat_rooms/", ChatRoomHandle.get),
        web.get("/chat_rooms/{chat_room_id}", ChatRoomHandle.get),
        web.post("/chat_room/", ChatRoomHandle.post),
        web.get("/messages/", MessageHandle.get),
        web.post("/message/", MessageHandle.post),
        web.get("/connect/{user_id}", ConnectHandle.get),
        web.post("/connect/", ConnectHandle.post),
        web.get("/comments/{message_id}", CommentHandle.get),
        web.post("/comment/", CommentHandle.post),

    ]
)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
    web.run_app(app, host=settings.api.host, port=settings.api.port)
