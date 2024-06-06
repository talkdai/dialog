# *-* coding: utf-8 *-*
import datetime
import logging
from pydantic import parse_obj_as

from dialog.db import engine, get_session
from dialog.settings import Settings
from dialog.schemas import ChatModel, SessionModel, SessionsModel
from dialog.llm import process_user_message, add_langserve_routes
from dialog_lib.db.memory import get_messages
from dialog_lib.db.models import Chat as ChatEntity

from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, status, Depends
from dialog_lib.db.utils import create_chat_session as db_create_session

api_router = APIRouter()


@api_router.post("/chat/{chat_id}")
async def post_message(chat_id: str, message: ChatModel, session: Session = Depends(get_session)):
    """
    Endpoint to post a message to a certain chat id.

    This endpoint will use the LLM to process the message and return the response.
    """
    chat_obj = session.query(ChatEntity).filter(ChatEntity.session_id == chat_id).first()
    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )
    start_time = datetime.datetime.now()
    ai_message = process_user_message(message.message, chat_id)
    duration = datetime.datetime.now() - start_time
    logging.info(f"Request processing time for chat_id {chat_id}: {duration}")
    return {"message": ai_message["text"]}


@api_router.post("/ask")
async def ask_question_to_llm(message: ChatModel, session: Session = Depends(get_session)):
    """
    This posts a single message to the LLM and returns the response without
    using memory.
    """
    start_time = datetime.datetime.now()
    ai_message = process_user_message(message.message, chat_id=None)
    duration = datetime.datetime.now() - start_time
    logging.info(f"Request processing time: {duration}")
    return {"message": ai_message["text"]}


@api_router.get("/chat/{chat_id}")
async def get_chat_content(chat_id, session: Session = Depends(get_session)):
    """
    Endpoint to fetch all messages from a certain chat id.
    """
    chat_obj = session.query(ChatEntity).filter(ChatEntity.session_id == chat_id).first()

    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat ID not found",
        )

    messages = get_messages(chat_id, dbsession=session, database_url=Settings().DATABASE_URL)
    return {"message": messages}


@api_router.post("/session")
async def create_chat_session_view(session: SessionModel | None = None, dbsession: Session = Depends(get_session)):
    """
    Endpoint to create a new chat session.
    """
    identifier = None
    if session:
        identifier = session.chat_id
    return db_create_session(identifier=identifier, dbsession=dbsession)


@api_router.get("/sessions")
async def get_sessions(session: Session = Depends(get_session)) -> SessionsModel:
    """
    Endpoint to get all chat sessions.
    """
    sessions = session.query(ChatEntity).all()
    return parse_obj_as(SessionsModel, {"sessions": [
        SessionModel.model_validate({
            "chat_id": str(s.session_id) # TODO: Make model dump, instead of dict
        }) for s in sessions
    ]})