import os
import pytest
import responses
import sqlalchemy

from uuid import uuid4
from dialog.models import Chat
from unittest.mock import patch
from fastapi.testclient import TestClient
from dialog.models.db import session
from dialog.models.helpers import create_session

@pytest.fixture()
def client():
    from main import app
    with TestClient(app) as client:
        yield client

@pytest.fixture()
def session_id(client):
    response = client.post("/session")
    return response.json()["chat_id"]

@pytest.fixture()
def chat_session():
    return create_session()

@pytest.fixture(autouse=True)
def dbsession():
    yield session
