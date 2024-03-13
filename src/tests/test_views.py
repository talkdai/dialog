import unittest
import responses

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Dialogue API is healthy"}

def test_create_session(client, mocker):
    response = client.post("/session")
    assert response.status_code == 200
    assert "chat_id" in response.json()

def test_post_message_no_session_id(client, mocker):
    llm_mock = mocker.patch('main.post_message.get_llm_class')
    llm_mock.return_value = mocker.Mock()
    response = client.post("/chat/lala", json={"message": "Hello"})
    assert llm_mock.called
    assert response.status_code == 200


# def test_post_message_no_session_id(self):
#     response = client.post("/ask", json={"message": "Hello"})
#     self.assertEqual(response.status_code, 200)
#     self.assertIn("message", response.json())

# def test_get_chat_content(self):
#     response = client.get(f"/chat/{self.session_id}")
#     self.assertEqual(response.status_code, 200)
#     self.assertIn("message", response.json())

