# *-* coding: utf-8 *-*
import datetime
import logging

from typing import Optional

from importlib_metadata import entry_points

from dialog.llm import get_llm_class
from dialog.llm.memory import get_messages
from dialog.models import Chat as ChatEntity
from dialog.models.db import engine, session
from dialog.settings import (
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    LOGGING_LEVEL,
    PROJECT_CONFIG,
    STATIC_FILE_LOCATION,
    CORS_ALLOW_ORIGINS
)

from sqlalchemy import text
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from dialog.models.helpers import create_session as db_create_session
from fastapi.staticfiles import StaticFiles

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

app.mount("/static", StaticFiles(directory=STATIC_FILE_LOCATION), name="static")

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


@app.post("/ask")
async def post_message_no_memory(message: Chat):
    start_time = datetime.datetime.now()
    LLM = get_llm_class()
    llm_instance = LLM(config=PROJECT_CONFIG)
    ai_message = llm_instance.process(message.message)
    duration = datetime.datetime.now() - start_time
    logging.info(f"Request processing time: {duration}")
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


class Session(BaseModel):
    chat_id: str


@app.post("/session")
async def create_session(session: Session | None = None):
    identifier = None
    if session:
        identifier = session.chat_id
    return db_create_session(identifier=identifier)


plugins = entry_points(group="dialog")
for plugin in plugins:
    logging.info("Loading plugin: %s", plugin.name)
    try:
        plugin_module = plugin.load()
    except ImportError:
        logging.warning("Failed to load plugin: %s.", plugin.name)
    else:
        try:
            plugin_module.register_plugin(app)
        except AttributeError:
            logging.warning("Failed to register plugin: %s", plugin.name)
