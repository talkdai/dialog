import logging
import importlib

from typing import Type

from .default import DialogLLM
from dialog_lib.agents.abstract import AbstractLLM
from dialog.settings import Settings


def get_llm_class() -> Type[AbstractLLM]:
    if Settings().LLM_CLASS is None:
        return DialogLLM

    llm_class = None

    try:
        module, class_name = Settings().LLM_CLASS.rsplit(".", 1)
        llm_module = importlib.import_module(module)
        llm_class = getattr(llm_module, class_name)
    except Exception as e:
        logging.info(f"Failed to load LLM class {Settings().LLM_CLASS}. Using default LLM. Exception: {e}")

    return llm_class or DialogLLM