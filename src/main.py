# *-* coding: utf-8 *-*
import uuid

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from llm import process_user_intent
from llm.memory import get_messages
from models import Chat as ChatEntity
from models.db import engine, session
from pydantic import BaseModel
from sqlalchemy import text

app = FastAPI(
    title="Dialog API",
    description="Humanized Conversation API (using LLM)",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Chat(BaseModel):
    message: str


@app.get("/health")
async def health():
    with engine.connect() as con:
        try:
            con.execute(text('SELECT 1'))
            return {"message": "Dialogue API is healthy"}
        except:
            return {"message": "Failed to execute simple SQL"}


@app.post("/chat/{chat_id}")
async def post_message(chat_id: str, message: Chat):
    chat_obj = session.query(ChatEntity).filter(
        ChatEntity.uuid == chat_id
    ).first()

    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )

    ai_message = process_user_intent(chat_id, message.message)
    return {"message": ai_message["text"]}

@app.get("/chat/{chat_id}")
async def get_chat_content(chat_id):
    chat_obj = session.query(ChatEntity).filter(
        ChatEntity.uuid == chat_id
    ).first()

    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )

    messages = get_messages(chat_id)
    return {"message": messages}


@app.post("/session")
async def create_session():
    session_uuid = uuid.uuid4().hex
    chat = ChatEntity(uuid=session_uuid)
    session.add(chat)
    session.commit()
    return {"chat_id": session_uuid}
