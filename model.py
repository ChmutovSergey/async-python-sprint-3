from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer
from sqlalchemy import sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class BaseModelMixin:
    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())

    def to_dict(self):
        return {
            "id": str(self.id),
            "created_at": self.created_at.timestamp(),
        }


class UserModel(Base, BaseModelMixin):
    __tablename__ = "users"

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship("MessageModel", backref="user")
    comments = relationship("CommentModel", backref="user")

    @property
    def to_dict(self):
        base_field = super().to_dict()
        base_field.update({"name": self.name})
        return base_field


class ChatRoomModel(Base, BaseModelMixin):
    __tablename__ = "chat_rooms"

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship("MessageModel", backref="chat")

    def __repr__(self):
        return f"ChatRoom {self.name}"

    @property
    def to_dict(self):
        base_field = super().to_dict()
        base_field.update({"name": self.name})
        return base_field


class ConnectedChatRoomModel(Base, BaseModelMixin):
    __tablename__ = "connected_chat_rooms"

    user_id = Column(Integer, ForeignKey("users.id"))
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"))

    @property
    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "chat_room_id": str(self.chat_room_id),
        }


class MessageModel(Base, BaseModelMixin):
    __tablename__ = "messages"

    message = Column(VARCHAR(255), nullable=False)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    comments = relationship("CommentModel", backref="message")

    def __repr__(self):
        return f"Author {self.author} message {self.message}"

    @property
    def to_dict(self):
        base_field = super().to_dict()
        base_field.update({
            "message": self.message,
            "chat_room_id": str(self.chat_room_id),
            "author_id": str(self.author_id),
        })
        return base_field


class CommentModel(Base, BaseModelMixin):
    __tablename__ = "comments"

    comment = Column(VARCHAR(255), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"))
    author_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return f"Author {self.author} comment {self.comment}"

    @property
    def to_dict(self):
        base_field = super().to_dict()
        base_field.update({
            "comment": self.comment,
            "message_id": str(self.message_id),
            "author_id": str(self.author_id),
        })
        return base_field
