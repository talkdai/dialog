from .db import engine

from pgvector.sqlalchemy import Vector

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, mapped_column
Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"

    uuid = Column(String, primary_key=True)
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    uuid = Column(String, primary_key=True)
    chat_id = mapped_column(ForeignKey("chats.uuid"))
    chat = relationship("Chat", back_populates="messages")


class CompanyContent(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True)
    question = Column(String)
    content = Column(String)
    chat_id = Column(Integer)


# if __name__ == "__main__":
Base.metadata.create_all(engine)
