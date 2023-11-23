from sqlalchemy.orm import declarative_base
from sqlalchemy import Table

from .db import engine

Base = declarative_base()


class Chat(Base):
    __table__ = Table(
        "chats",
        Base.metadata,
        psql_autoload=True,
        autoload_with=engine,
        extend_existing=True
    )


class ChatMessages(Base):
    __table__ = Table(
        "chat_messages",
        Base.metadata,
        psql_autoload=True,
        autoload_with=engine,
        extend_existing=True
    )


class CompanyContent(Base):
    __table__ = Table(
        "contents",
        Base.metadata,
        psql_autoload=True,
        autoload_with=engine,
        extend_existing=True
    )
