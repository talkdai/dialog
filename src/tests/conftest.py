import os
import pytest
import tomllib
import dotenv

from main import app
from dialog_lib.db.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dialog_lib.db.utils import create_chat_session
from dialog.db import get_session
from dialog.routers.models import add_model_router
from pathlib import Path

dotenv.load_dotenv()

SQLALCHEMY_DATABASE_URL = "postgresql://talkdai:talkdai@db/test_talkdai"

TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')
if TEST_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL


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
def client_with_settings_override(dbsession, mocker, monkeypatch):
    def get_session_override():
        return dbsession

    settings = tomllib.loads(Path("/app/src/tests/fixtures/multi_model.toml").read_text())

    blob_model = settings["endpoint"][0]

    mocker.patch("main.Settings.PROJECT_CONFIG", return_value=settings, new_callable=mocker.PropertyMock)

    monkeypatch.setenv("PROJECT_CONFIG", "/app/src/tests/fixtures/multi_model.toml")

    main_app = app

    add_model_router(
        main_app,
        blob_model["model_class_path"],
        blob_model.get("path")
    )
    with TestClient(main_app) as client:
        main_app.dependency_overrides[get_session] = get_session_override
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

@pytest.fixture
def llm_mock_openai_router(mocker):
    llm_mock = mocker.patch('dialog.routers.openai.process_user_message')
    llm_mock.return_value = {"text": "Hello"}
    return llm_mock