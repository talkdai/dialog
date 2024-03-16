import logging
import importlib

from typing import Type

from .default import DialogLLM
from .abstract_llm import AbstractLLM
from dialog.settings import OPENAI_API_KEY, LLM_CLASS


def get_llm_class() -> Type[AbstractLLM]:
    if LLM_CLASS is None:
        return DialogLLM

    llm_class = None

    try:
        module, class_name = LLM_CLASS.rsplit(".", 1)
        llm_module = importlib.import_module(module)
        llm_class = getattr(llm_module, class_name)
    except Exception as e:
        logging.info(f"Failed to load LLM class {LLM_CLASS}. Using default LLM")

    return llm_class or DialogLLM