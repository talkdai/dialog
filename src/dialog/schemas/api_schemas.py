from pydantic import BaseModel, ConfigDict

class ChatModel(BaseModel):
    message: str


class SessionModel(BaseModel):
    chat_id: str

class SessionsModel(BaseModel):
    sessions: list[SessionModel]


class ContentModel(BaseModel):
    question: str
    content: str