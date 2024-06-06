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

def add_model_router(app, model_class_path, model_path=None):
    model_router = APIRouter()

    @model_router.post("/chat/{chat_id}")
    async def post_message_models(chat_id: str, message: ChatModel, session: Session = Depends(get_session)):
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
        ai_message = process_user_message(message.message, chat_id, model_class_path=model_class_path)
        duration = datetime.datetime.now() - start_time
        logging.info(f"Request processing time for chat_id {chat_id}: {duration}")
        return {"message": ai_message["text"]}


    @model_router.post("/ask")
    async def ask_question_to_llm_model(message: ChatModel, session: Session = Depends(get_session)):
        """
        This posts a single message to the LLM and returns the response without
        using memory.
        """
        start_time = datetime.datetime.now()
        ai_message = process_user_message(message.message, chat_id=None, model_class_path=model_class_path)
        duration = datetime.datetime.now() - start_time
        logging.info(f"Request processing time: {duration}")
        return {"message": ai_message["text"]}

    add_langserve_routes(model_router, path=model_path)
    app.include_router(model_router, prefix=model_path)