import asyncio

from aiohttp import web

from config.config import settings
from db_worker.worker import DBWorker
from server.views import UserView, ChatRoomView, MessageView, CommentView, ConnectView


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
