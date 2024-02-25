import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestViewsAPI(unittest.TestCase):
    # TODO: Mock requests to LLM and DB
    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Dialogue API is healthy"})
        
    def test_post_message(self):
        response = client.post(f"/chat/{self.session_id}", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_post_message_no_session_id(self):
        response = client.post("/ask", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_get_chat_content(self):
        response = client.get(f"/chat/{self.session_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

