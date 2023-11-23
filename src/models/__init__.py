from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import Table, MetaData
from .db import engine, Base

from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

from .db import Base

metadata = MetaData()
metadata.bind = engine
try:
    class ChatMessages(Base):
        __table__ = Table(
            'chat_messages', metadata,  autoload_with=engine
        )
        __tablename__ = 'chat_messages'


except NoSuchTableError:
    ChatMessages = None

try:
    class Chat(Base):
        __table__ = Table(
            'chats', metadata,  autoload_with=engine
        )
        __tablename__ = 'chats'


except NoSuchTableError:
    Chat = None


try:
    class CompanyContent(Base):
        __table__ = Table(
            'contents',
            metadata,
            autoload_with=engine
        )
        __tablename__ = 'contents'

    CompanyContent.__table__.columns["embedding"].type = Vector(1536)


except NoSuchTableError:
    CompanyContent = None