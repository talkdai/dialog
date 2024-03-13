from dialog.models import ChatMessages

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Dialogue API is healthy"}

def test_create_session(client, mocker):
    response = client.post("/session")
    assert response.status_code == 200
    assert "chat_id" in response.json()

def test_post_message_no_session_id(client, chat_session, mocker):
    llm_mock = mocker.patch('main.get_llm_class')
    llm_mock.process.return_value = {"text": "Hello"}
    session_id = chat_session["chat_id"]
    response = client.post(f"/chat/{session_id}", json={"message": "Hello"})
    assert llm_mock.called
    assert response.status_code == 200
    assert "message" in response.json()


def test_ask_question_no_session_id(client, chat_session, mocker):
    llm_mock = mocker.patch('main.get_llm_class')
    llm_mock.process.return_value = {"text": "Hello"}
    response = client.post("/ask", json={"message": "Hello"})
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_chat_content(client, chat_session, dbsession):
    chat = ChatMessages(session_id=chat_session["chat_id"], message="Hello")
    dbsession.add(chat)
    response = client.get(f"/chat/{chat_session['chat_id']}")
    assert response.status_code == 200
    assert "message" in response.json()