from .db import engine

from pgvector.sqlalchemy import Vector

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)


class CompanyContent(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True)
    question = Column(String)
    content = Column(String)
    chat_id = Column(Integer)


# if __name__ == "__main__":
Base.metadata.create_all(engine)
