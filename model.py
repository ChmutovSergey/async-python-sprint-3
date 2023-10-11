from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy import VARCHAR, TIMESTAMP, Column, ForeignKey
from sqlalchemy import sql, text, func
from sqlalchemy.dialects.postgresql import UUID


@as_declarative()
class Base:
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())
    created_by = Column(VARCHAR(255), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.current_timestamp())
    updated_by = Column(VARCHAR(255), nullable=True)

    @declared_attr
    def __tablename__(cls):  # noqa 805
        return cls.__name__.lower()


class UserModel(Base):
    __tablename__ = "users"

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship("MessageModel", backref="user")
    comments = relationship("CommentModel", backref="user")


class ChatRoomModel(Base):
    __tablename__ = "chat_rooms"

    name = Column(VARCHAR(255), nullable=False)
    messages = relationship("MessageModel", backref="chat")

    def __repr__(self):
        return f"ChatRoom {self.name}"


class MessageModel(Base):
    __tablename__ = "messages"

    message = Column(VARCHAR(255), nullable=False)
    chat_room_id = Column(UUID(as_uuid=True), ForeignKey("chat_rooms.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    comments = relationship("CommentModel", backref="message")

    def __repr__(self):
        return f"Author {self.author} message {self.message}"

    @property
    def to_dict(self):
        return {
            "id": str(self.id),
            "message": self.message,
            "chat_room_id": str(self.chat_room_id),
            "author_id": str(self.author_id),
            "created_at": self.created_at.timestamp(),
        }


class CommentModel(Base):
    __tablename__ = "comments"

    comment = Column(VARCHAR(255), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    def __repr__(self):
        return f"Author {self.author} comment {self.comment}"
