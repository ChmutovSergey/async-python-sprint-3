import asyncio
from aiohttp import web

from config.config import settings
from db_worker.worker import DBWorker
from server.views import UserView, ChatRoomView, MessageView, CommentView, ConnectView


# class UserView:
#
#     @staticmethod
#     async def get(request):
#         async with async_session() as session, session.begin():
#             stmt = select(UserModel)
#             if user_id := request.match_info.get("user_id"):
#                 stmt = stmt.filter(UserModel.id == user_id)
#             user_list = await session.execute(stmt)
#             users_list_obj = []
#             for a1 in user_list.scalars():
#                 users_list_obj.append(a1.to_dict)
#             users_json = json.dumps(users_list_obj)
#         return web.json_response(body=users_json.encode())
#
#     @staticmethod
#     async def post(request):
#         body = await request.json()
#         if name := body.get("name"):
#             user = UserModel(name=name)
#             async with async_session() as session, session.begin():
#                 session.add(user)
#                 await session.commit()
#             return web.json_response(status=201)
#         return web.json_response(status=400)


# class ChatRoomView:
#     @staticmethod
#     async def get(request):
#         async with async_session() as session, session.begin():
#             stmt = select(ChatRoomModel)
#             if chat_room_id := request.match_info.get("chat_room_id"):
#                 stmt = stmt.filter(ChatRoomModel.id == chat_room_id)
#             chat_rooms_list = await session.execute(stmt)
#             chat_rooms_list_obj = []
#             for a1 in chat_rooms_list.scalars():
#                 chat_rooms_list_obj.append(a1.to_dict)
#             chat_rooms_json = json.dumps(chat_rooms_list_obj)
#         return web.json_response(body=chat_rooms_json.encode())
#
#     @staticmethod
#     async def post(request):
#         body = await request.json()
#         if name := body.get("name"):
#             chat_room = ChatRoomModel(name=name)
#             async with async_session() as session, session.begin():
#                 session.add(chat_room)
#                 await session.commit()
#             return web.json_response(status=201)
#         return web.json_response(status=400)
#
#
# class ConnectView:
#     @staticmethod
#     async def get(request):
#         user_id = request.match_info.get("user_id")
#         async with async_session() as session, session.begin():
#             stmt = select(ConnectedChatRoomModel).filter(
#                 ConnectedChatRoomModel.user_id == user_id,
#             )
#             chat_rooms_list = await session.execute(stmt)
#             chat_rooms_list_obj = []
#             for a1 in chat_rooms_list.scalars():
#                 chat_rooms_list_obj.append(a1.to_dict)
#             chat_rooms_json = json.dumps(chat_rooms_list_obj)
#         return web.json_response(body=chat_rooms_json.encode())
#
#     @staticmethod
#     async def post(request):
#         body = await request.json()
#         try:
#             value = ConnectedChatRoomSchema(**body)
#             async with async_session() as session, session.begin():
#                 session.add(ConnectedChatRoomModel(**value.__dict__))
#                 await session.commit()
#         except pydantic.error_wrappers.ValidationError as e:
#             return web.json_response(status=400, body=str(e).encode())
#         else:
#             return web.json_response(status=201)
#
#
# class MessageView:
#
#     @staticmethod
#     async def get(request):
#         body = await request.json()
#         try:
#             value = MassageGetSchema(**body)
#         except pydantic.error_wrappers.ValidationError as e:
#             return web.json_response(status=400, body=str(e).encode())
#
#         chat = ChatRoom(user=value.author_id, chat_room=value.chat_room_id)
#         connect_to_chat_at = await chat.check_connect()
#
#         if connect_to_chat_at:
#             message = Message(
#                 author=value.author_id,
#                 chat_room=value.chat_room_id,
#                 connect_to_chat_at=connect_to_chat_at,
#                 message_data=value)
#             message_json = await message.sent_message_for_client()
#
#             return web.json_response(body=message_json.encode())
#
#     @staticmethod
#     async def post(request):
#         body = await request.json()
#         try:
#             message = MassageCreateSchema(**body)
#             async with async_session() as session, session.begin():
#                 session.add(MessageModel(**message.__dict__))
#                 await session.commit()
#         except pydantic.error_wrappers.ValidationError as e:
#             return web.json_response(status=400, body=str(e).encode())
#         finally:
#             return web.json_response(status=201)
#
#
# class CommentView:
#
#     @staticmethod
#     async def get(request):
#         async with async_session() as session, session.begin():
#             stmt = select(CommentModel)
#             if message_id := request.match_info.get("message_id"):
#                 stmt = stmt.filter(CommentModel.message_id == message_id)
#             comment_list = await session.execute(stmt)
#             comment_list_obj = []
#             for a1 in comment_list.scalars():
#                 comment_list_obj.append(a1.to_dict)
#             comments_json = json.dumps(comment_list_obj)
#         return web.json_response(body=comments_json.encode())
#
#     @staticmethod
#     async def post(request):
#         body = await request.json()
#         try:
#             comment = CommentCreateSchema(**body)
#             async with async_session() as session, session.begin():
#                 session.add(CommentModel(**comment.__dict__))
#                 await session.commit()
#         except pydantic.error_wrappers.ValidationError as e:
#             return web.json_response(status=400, body=str(e).encode())
#         finally:
#             return web.json_response(status=201)


app = web.Application()
app.add_routes(
    [
        web.get("/users/", UserView.get),
        web.get("/users/{user_id}", UserView.get),
        web.post("/user/", UserView.post),
        web.get("/chat_rooms/", ChatRoomView.get),
        web.get("/chat_rooms/{chat_room_id}", ChatRoomView.get),
        web.post("/chat_room/", ChatRoomView.post),
        web.get("/messages/", MessageView.get),
        web.post("/message/", MessageView.post),
        web.get("/connect/{user_id}", ConnectView.get),
        web.post("/connect/", ConnectView.post),
        web.get("/comments/{message_id}", CommentView.get),
        web.post("/comment/", CommentView.post),
    ]
)


if __name__ == "__main__":
    db_worker = DBWorker()
    asyncio.run(db_worker.create_tables())
    web.run_app(app, host=settings.api.host, port=settings.api.port)
