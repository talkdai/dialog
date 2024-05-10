import os
import pytest

from main import app
from dialog_lib.db.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dialog_lib.db.utils import create_chat_session
from dialog.db import get_session

SQLALCHEMY_DATABASE_URL = "postgresql://talkdai:talkdai@db/test_talkdai"

@pytest.fixture
def dbsession(mocker):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session() as session:
        yield session
        session.rollback()

    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(dbsession):
    def get_session_override():
        return dbsession

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

@pytest.fixture
def session_id(client):
    response = client.post("/session")
    return response.json()["chat_id"]

@pytest.fixture
def chat_session(dbsession):
    return create_chat_session(dbsession=dbsession)

@pytest.fixture
def llm_mock(mocker):
    llm_mock = mocker.patch('dialog.routers.dialog.process_user_message')
    llm_mock.process.return_value = {"text": "Hello"}
    return llm_mock