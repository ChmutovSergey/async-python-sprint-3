import json

import pydantic
from aiohttp import web
from sqlalchemy.engine.result import ChunkedIteratorResult

from server.controller import (
    UserModelController,
    ChatRoomController,
    PeerController,
    CommentController,
    MessageController,
)


class BaseView:

    @staticmethod
    async def get_body(data: ChunkedIteratorResult) -> bytes:
        bodies_obj = []
        for res in data.scalars():
            bodies_obj.append(res.to_dict)
        body_json = json.dumps(bodies_obj)

        return body_json.encode()


class UserView(BaseView):

    async def get(self, request):
        user_id = request.match_info.get("user_id")
        user_list = await UserModelController().get_data_by_id(user_id)
        body = await self.get_body(user_list)
        return web.json_response(body=body)

    @staticmethod
    async def post(request):
        body = await request.json()
        if name := body.get("name"):
            await UserModelController().post_data_by_name(name)
            return web.json_response(status=201)
        return web.json_response(status=400)


class ChatRoomView(BaseView):

    async def get(self, request):
        chat_room_id = request.match_info.get("chat_room_id")
        chat_rooms_list = await ChatRoomController().get_data_by_id(chat_room_id)
        body = await self.get_body(chat_rooms_list)
        return web.json_response(body=body)

    @staticmethod
    async def post(request):
        body = await request.json()
        if name := body.get("name"):
            await ChatRoomController().post_data_by_name(name)
            return web.json_response(status=201)
        return web.json_response(status=400)


class PeerView(BaseView):

    async def get(self, request):
        user_id = request.match_info.get("user_id")
        chat_rooms_list = await PeerController().get_chat_room_by_user_id(user_id)
        body = await self.get_body(chat_rooms_list)
        return web.json_response(body=body)

    @staticmethod
    async def post(request):
        body = await request.json()
        try:
            await PeerController().commit_data(body)
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())
        else:
            return web.json_response(status=201)


class MessageView:

    @staticmethod
    async def get(request):
        body = await request.json()
        try:
            message_json = await MessageController().send_message(body)
            return web.json_response(body=message_json.encode())
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())

    @staticmethod
    async def post(request):
        body = await request.json()
        try:
            await MessageController().commit_data(body)
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())
        else:
            return web.json_response(status=201)


class CommentView(BaseView):

    async def get(self, request):
        message_id = request.match_info.get("message_id")
        comment_list = await CommentController().get_chat_room_by_user_id(message_id)
        body = await self.get_body(comment_list)
        return web.json_response(body=body)

    @staticmethod
    async def post(request):
        body = await request.json()
        try:
            await CommentController().commit_data(body)
        except pydantic.error_wrappers.ValidationError as e:
            return web.json_response(status=400, body=str(e).encode())
        else:
            return web.json_response(status=201)
