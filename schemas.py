from pydantic import BaseModel


class MassageCreateSchema(BaseModel):
    message: str
    chat_room_id: int
    author_id: int


class MassageGetSchema(BaseModel):
    chat_room_id: int
    author_id: int
    get_message_from: float | None
    get_message_to: float | None


class CommentCreateSchema(BaseModel):
    comment: str
    message_id: int
    author_id: int


class ConnectedChatRoomSchema(BaseModel):
    chat_room_id: int
    user_id: int
