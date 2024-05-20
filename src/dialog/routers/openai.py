# *-* coding: utf-8 *-*
from uuid import uuid4
import datetime
import logging

from dialog.db import engine, get_session
from dialog_lib.db.models import Chat as ChatEntity, ChatMessages
from dialog.schemas import OpenAIChat, OpenAIChatCompletion, OpenAIModel
from dialog.llm import process_user_message

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

open_ai_api_router = APIRouter()

@open_ai_api_router.get("/models")
async def get_models():
    """
    Returns the model that is available inside Dialog in the OpenAI format.
    """
    return [OpenAIModel(**{
        "id": "talkd-ai",
        "object": "model",
        "created": int(datetime.datetime.now().timestamp()),
        "owned_by": "system"
    })]

@open_ai_api_router.post("/chat/completions")
async def ask_question_to_llm(message: OpenAIChat, session: Session = Depends(get_session)):
    """
    This posts a message to the LLM and returns the response in the OpenAI format.
    """
    start_time = datetime.datetime.now()
    new_chat = ChatEntity(
        session_id = f"openai-{str(uuid4())}",
    )
    session.add(new_chat)
    for message in message.messages[:-1]:
        new_message = ChatMessages(
            session_id=new_chat.session_id,
            message=message.message,
        )
        session.add(new_message)
    session.flush()

    ai_message = process_user_message(message.messages[-1].content, chat_id=new_chat.session_id)

    duration = datetime.datetime.now() - start_time
    logging.info(f"Request processing time: {duration}")
    chat_completion = OpenAIChatCompletion(
        choices=[
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
        created=int(datetime.datetime.now().timestamp()),
        id=f"talkdai-{str(uuid4())}",
        model="talkdai",
        object="chat.completion",
        usage={
            "completion_tokens": None,
            "prompt_tokens": None,
            "total_tokens": None
        }
    )
    return chat_completion