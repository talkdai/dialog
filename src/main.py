# *-* coding: utf-8 *-*
import datetime
import logging

from importlib_metadata import entry_points

from dialog.models.db import engine
from dialog.settings import (
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    LOGGING_LEVEL,
    PROJECT_CONFIG,
    STATIC_FILE_LOCATION,
    CORS_ALLOW_ORIGINS,
)

from sqlalchemy import text
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from dialog.chains.rag_chain import get_rag_chain, get_rag_chain_with_memory
from dialog.memory.postgres_memory import CustomPostgresChatMessageHistory

logging.basicConfig(
    level=LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
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


class Message(BaseModel):
    content: str

class Session(BaseModel):
    chat_id: str


@app.get("/health")
async def health():
    with engine.connect() as con:
        try:
            con.execute(text("SELECT 1"))
            return {"message": "Dialogue API is healthy"}
        except:
            return {"message": "Failed to execute simple SQL"}


@app.post("/chat/{chat_id}")
async def post_message(chat_id: str, message: Message):
    # Get the answer from the RAG model using the memory history,
    # which itself is contextualized together with the question to make a standalone question
    memory = CustomPostgresChatMessageHistory(session_id=chat_id)
    history = await memory.aget_messages()
    inputs = {
        "question": message.content,
        "chat_history": history
        
    }
    rag_chain_with_memory = get_rag_chain_with_memory()
    answer = rag_chain_with_memory.invoke(inputs)
    
    # Save the question and answer to the memory
    memory.add_user_message(message.content)
    memory.add_ai_message(answer)
    
    return {"message": answer.content}


@app.post("/ask")
async def post_message_no_memory(message: Message):
    rag_chain = get_rag_chain()
    answer = rag_chain.invoke(message.content)
    return {"message": answer}


@app.get("/chat/{chat_id}")
async def get_chat_content(chat_id):
    memory = CustomPostgresChatMessageHistory(session_id=chat_id)
    history = await memory.aget_messages()
    return {"messages": [{"content": message.content, "sender": message.type} for message in history]}


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
