from abc import ABCMeta
import json

import pydantic
from aiohttp import web
from sqlalchemy.future import select

from config.session import async_session
from model import ChatRoomModel, CommentModel, ConnectedChatRoomModel, MessageModel, UserModel
from schemas import CommentCreateSchema, ConnectedChatRoomSchema, MassageCreateSchema, MassageGetSchema
from server.chat_handler import ChatRoom
from server.message_handler import Message


class AbstractView(ABCMeta):
    @staticmethod
    async def get(request):
        pass

    @staticmethod
    async def post(request):
        pass


class UserView(AbstractView):
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


class ChatRoomView(AbstractView):
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


class ConnectView(AbstractView):
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


class MessageView(AbstractView):

    @staticmethod
    async def get(request):
        body = await request.json()
        try:
            value = MassageGetSchema(**body)
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())

        chat = ChatRoom(user=value.author_id, chat_room=value.chat_room_id)
        connect_to_chat_at = await chat.check_connect()

        if connect_to_chat_at:
            message = Message(
                author=value.author_id,
                chat_room=value.chat_room_id,
                connect_to_chat_at=connect_to_chat_at,
                message_data=value)
            message_json = await message.sent_message_for_client()

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


class CommentView(AbstractView):

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
