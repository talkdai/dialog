# *-* coding: utf-8 *-*
import datetime
import importlib
import logging

from copy import copy

from llm import get_llm_class
from llm.memory import get_messages
from models import Chat as ChatEntity
from models.db import engine, session

from settings import LOGGING_LEVEL, PLUGINS, PROJECT_CONFIG

from sqlalchemy import text
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models.helpers import create_session as db_create_session
from webhooks.router import router


logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Dialog API",
    description="Humanized Conversation API (using LLM)",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/webhooks", tags=["webhooks"])

class Chat(BaseModel):
    message: str


@app.get("/health")
async def health():
    with engine.connect() as con:
        try:
            con.execute(text("SELECT 1"))
            return {"message": "Dialogue API is healthy"}
        except:
            return {"message": "Failed to execute simple SQL"}


@app.post("/chat/{chat_id}")
async def post_message(chat_id: str, message: Chat):
    chat_obj = session.query(ChatEntity).filter(ChatEntity.uuid == chat_id).first()

    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )
    start_time = datetime.datetime.now()
    LLM = get_llm_class()
    llm_instance = LLM(config=PROJECT_CONFIG, session_id=chat_id)
    ai_message = llm_instance.process(message.message)
    duration = datetime.datetime.now() - start_time
    logging.info(f"Request processing time for chat_id {chat_id}: {duration}")
    return {"message": ai_message["text"]}


@app.get("/chat/{chat_id}")
async def get_chat_content(chat_id):
    chat_obj = session.query(ChatEntity).filter(ChatEntity.uuid == chat_id).first()

    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )

    messages = get_messages(chat_id)
    return {"message": messages}


@app.post("/session")
async def create_session():
    return db_create_session()


for plugin in PLUGINS:
    try:
        logging.info(f"Loading plugin: {plugin}")
        plugin_module = importlib.import_module(plugin)
    except ImportError:
        logging.warning(f"Failed to import plugin {plugin}")

    try:
        app.include_router(plugin_module.router)
    except AttributeError:
        logging.warning(f"Failed to add Plugin: {plugin} to main router")