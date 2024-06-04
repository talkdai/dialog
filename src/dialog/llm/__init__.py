import logging
import importlib

from typing import Type

from dialog_lib.agents.abstract import AbstractLLM
from dialog.settings import Settings

from langserve import add_routes
from langchain_core.runnables.base import RunnableBindingBase

from .agents.default import *
from .agents.lcel import *


def get_llm_class(model_class_path=None):
    if Settings().LLM_CLASS is None and model_class_path is None:
        return DialogLLM

    llm_class = None

    runnable_to_fetch = model_class_path or Settings().LLM_CLASS

    try:
        module, class_name = runnable_to_fetch.rsplit(".", 1)
        llm_module = importlib.import_module(module)
        llm_class = getattr(llm_module, class_name)
    except Exception as e:
        logging.info(f"Failed to load LLM class {runnable_to_fetch}. Raising Exception: {e}")
        raise

    if llm_class:
        return llm_class

    logging.info(f"Falling back on default Agent")
    return DialogLLM


def process_user_message(message, chat_id=None, model_class_path=None):
    llm_class = get_llm_class(model_class_path=model_class_path)

    if isinstance(llm_class, RunnableBindingBase):
        ai_message = llm_class.invoke(
            {"input": message},
            {"configurable": {
                "session_id": chat_id,
                "model": Settings().PROJECT_CONFIG.get("model_name", "gpt-3.5-turbo"),
                **Settings().PROJECT_CONFIG,
            }}
        )
        ai_message = {"text": ai_message.content}

    else:
        llm_instance = llm_class(config=Settings().PROJECT_CONFIG, session_id=chat_id)
        ai_message = llm_instance.process(message)

    return ai_message

def add_langserve_routes(app, path=None):
    llm_instance = get_llm_class()

    if isinstance(llm_instance, RunnableBindingBase):
        add_routes(app, llm_instance, path=path)