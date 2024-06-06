import os
import pytest

from dialog_lib.db.models import ChatMessages, Chat

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Dialog API is healthy"}

def test_create_chat_session(client, mocker):
    response = client.post("/session")
    assert response.status_code == 200
    assert "chat_id" in response.json()

def test_post_message_no_session_id(client, chat_session, mocker, llm_mock, dbsession):
    session_id = chat_session["chat_id"]
    response = client.post(f"/chat/{session_id}", json={"message": "Hello"})
    assert llm_mock.called
    assert response.status_code == 200
    assert "message" in response.json()


def test_ask_question_no_session_id(client, mocker, llm_mock, dbsession):
    response = client.post("/ask", json={"message": "Hello"})
    assert response.status_code == 200
    assert "message" in response.json()
    assert llm_mock.called
    assert dbsession.query(Chat).count() == 0

def test_get_chat_content(client, chat_session, dbsession):
    chat = ChatMessages(session_id=chat_session["chat_id"], message="Hello")
    dbsession.add(chat)
    dbsession.flush()
    response = client.get(f"/chat/{chat_session['chat_id']}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert dbsession.query(ChatMessages).count() == 1

def test_get_all_sessions(client, chat_session):
    response = client.get("/sessions")
    assert response.status_code == 200
    assert "sessions" in response.json()
    assert len(response.json()["sessions"]) == 1

def test_invalid_database_connection(client, mocker):
    mocker.patch("dialog.routers.dialog.engine.connect", side_effect=Exception)
    with pytest.raises(Exception):
        response = client.get("/health")
        assert response.status_code == 500
        assert response.json() == {"message": "Failed to execute simple SQL"}

# test openai router

def test_customized_openai_models_response(client):
    response = client.get("/openai/models")
    assert response.status_code == 200
    for i in ["id", "object", "created", "owned_by"]:
        assert i in response.json()[0]

def test_customized_openai_chat_completion_response_stream_false(client, llm_mock_openai_router):
    os.environ["LLM_CLASS"] = "dialog.llm.agents.default.DialogLLM"
    response = client.post("/openai/chat/completions", json={
        "model": "talkdai",
        "messages": [
            {
                "role": "user",
                "content": "Hello"
            }
        ],
        "stream": False
    })
    assert response.status_code == 200
    for i in ["choices", "created", "id", "model", "object", "usage"]:
        assert i in response.json()
    assert llm_mock_openai_router.called
    assert response.json()["choices"][0]["message"]["role"] == "assistant"


def test_multiple_models_load_on_setting_override(client_with_settings_override):
    response = client_with_settings_override.get("/openapi.json")
    assert response.status_code == 200
    assert "/custom_model/chat/{chat_id}" in list(response.json().get("paths").keys())
    assert "/custom_model/ask" in list(response.json().get("paths").keys())

def test_multiple_models_are_available_on_model_listing_for_webui(client_with_settings_override, mocker):
    # client_with_settings_override doesn't override Settings calling, so we need to override here
    mocker.patch("dialog.routers.openai.Settings.PROJECT_CONFIG", return_value={
        "endpoint": [{
            "model_class_path": "dialog.llm.agents.default.DialogLLM",
            "model_name": "custom-model",
            "path": "/custom_model"
        }]
    }, new_callable=mocker.PropertyMock)

    response = client_with_settings_override.get("/openai/models")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == "talkd-ai"
    assert response.json()[1]["id"] == "custom-model"