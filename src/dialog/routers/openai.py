# *-* coding: utf-8 *-*
from uuid import uuid4
import datetime
import logging

from dialog.db import engine, get_session
from dialog.schemas import ChatModel
from dialog.llm import process_user_message

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

open_ai_api_router = APIRouter()

@open_ai_api_router.get("/models")
async def get_models():
    """
    Returns the model that is available inside Dialog in the OpenAI format.
    """
    return [{
        "id": "talkd-ai",
        "object": "model",
        "created": datetime.datetime.now().timestamp(),
        "owned_by": "system"
    }]

@open_ai_api_router.post("/chat/completions")
async def ask_question_to_llm(message: ChatModel, session: Session = Depends(get_session)):
    """
    This posts a single message to the LLM and returns the response without
    using memory.
    """
    start_time = datetime.datetime.now()
    ai_message = process_user_message(message, chat_id=None)
    duration = datetime.datetime.now() - start_time
    logging.info(f"Request processing time: {duration}")
    return {
        "choices": [
            {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": ai_message["text"],
                "role": "assistant"
            },
            "logprobs": None
            }
        ],
        "created": datetime.datetime.now().timestamp(),
        "id": f"talkdai-{str(uuid4())}",
        "model": "talkdai",
        "object": "chat.completion",
        "usage": {
            "completion_tokens": None,
            "prompt_tokens": None,
            "total_tokens": None
        }
    }
