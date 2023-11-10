# *-* coding: utf-8 *-*
import uuid
from contextlib import asynccontextmanager

from decouple import config
from .models.db import session, engine
from .models import Chat as ChatEntity, CompanyContent
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from pydantic import BaseModel
from typing import Union, Optional, List, Dict, Any

from .llm import llm
from langchain.schema import HumanMessage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize csv
    yield
    # exits app


app = FastAPI(
    title="Dialogue API",
    description="Dialogue API for humanized AI",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
    email: Optional[str]
    name: Optional[str]
    message: str


# from langchain.memory import PostgresChatMessageHistory

# history = PostgresChatMessageHistory(
#     connection_string="postgresql://postgres:mypassword@localhost/chat_history",
#     session_id="foo",
# )

# history.add_user_message("hi!")

# history.add_ai_message("whats up?")



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
    # Check if chat_id exists
    chat_obj = session.query(ChatEntity).filter(
        ChatEntity.uuid == chat_id
    ).first()

    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )

    # Save message to db
    # Process message with langchain and
    return {"message": llm.invoke(message.message)}


@app.get("/chat")
async def get_chat_content():
    return {"message": "First FastAPI app"}


@app.post("/session")
async def create_session():
    session_uuid = uuid.uuid4().hex
    chat = ChatEntity(uuid=session_uuid)
    session.add(chat)
    session.commit()
    return {"chat_id": session_uuid}
