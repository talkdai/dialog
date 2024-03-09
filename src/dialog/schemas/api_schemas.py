from pydantic import BaseModel

class ChatModel(BaseModel):
    message: str


class SessionModel(BaseModel):
    chat_id: str