import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestViewsAPI(unittest.TestCase):
    # TODO: Mock requests to LLM and DB

    def setUp(self):
        session_resp = client.post("/session")
        session_resp_json = session_resp.json()
        self.session_id = session_resp_json["chat_id"]

    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Dialogue API is healthy"})

    def test_create_session(self):
        response = client.post("/session")
        self.assertEqual(response.status_code, 200)
        self.assertIn("chat_id", response.json())

    def test_post_message(self):
        response = client.post(f"/chat/{self.session_id}", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_get_chat_content(self):
        response = client.get(f"/chat/{self.session_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

