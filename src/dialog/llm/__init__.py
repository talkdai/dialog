import logging
import importlib

from typing import Type

from dialog_lib.agents.abstract import AbstractLLM
from dialog.settings import Settings

from langserve import add_routes
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables.base import RunnableSequence

from .agents.default import *
from .agents.lcel import *


def get_llm_class():
    if Settings().LLM_CLASS is None:
        return DialogLLM, "AbstractLLM"

    llm_class = None

    try:
        module, class_name = Settings().LLM_CLASS.rsplit(".", 1)
        llm_module = importlib.import_module(module)
        llm_class = getattr(llm_module, class_name)
    except Exception as e:
        logging.info(f"Failed to load LLM class {Settings().LLM_CLASS}. Using default LLM. Exception: {e}")
        raise

    if isinstance(llm_class, AbstractLLM):
        return llm_class, "AbstractLLM"

    elif 'langchain_core.runnables' in str(type(llm_class)):
        return llm_class, "LCELRunnable"

    logging.info(f"Type for LLM class is: {type(llm_class)}")

    return DialogLLM, "AbstractLLM"


def process_user_message(message, chat_id=None):
    LLM, llm_type = get_llm_class()
    if llm_type == "AbstractLLM":
        llm_instance = LLM(config=Settings().PROJECT_CONFIG, session_id=chat_id)
        ai_message = llm_instance.process(message.message)

    elif llm_type == "LCELRunnable":
        ai_message = LLM.invoke(
            {"input": message.message},
            {"configurable": {
                "session_id": chat_id,
                "model": Settings().PROJECT_CONFIG.get("model_name", "gpt-3.5-turbo"),
                **Settings().PROJECT_CONFIG,
            }}
        )
        ai_message = {"text": ai_message.content}

    return ai_message

def add_langserve_routes(app):
    llm_instance, llm_type = get_llm_class()

    if llm_type == "LCELRunnable":
        add_routes(app, llm_instance)