import uuid

from .db import engine, Base
from sqlalchemy import Table, MetaData
from sqlalchemy import (
    Column, Integer, DateTime, String, text, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector


class ChatMessages(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    parent = Column(Integer, nullable=True)
    session_id = Column(String, nullable=False)
    message = Column(JSONB, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Chat(Base):
    __tablename__ = "chats"

    uuid = Column(UUID, nullable=False, default=str(uuid.uuid4()), primary_key=True)
    tags = Column(String, nullable=True)

class CompanyContent(Base):
    __tablename__ = "contents"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    question = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    dataset = Column(String, nullable=True)
    link = Column(String, nullable=True)


