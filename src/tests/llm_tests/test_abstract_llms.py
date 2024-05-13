import os
import pytest

from dialog.llm import get_llm_class
from dialog_lib.agents.abstract import AbstractLLM
from dialog.llm.agents.default import DialogLLM
from dialog.llm import DialogLLM


def test_abstract_llm_for_invalid_config():
    with pytest.raises(ValueError):
        AbstractLLM(1)

def test_abstract_llm_with_valid_config():
    config = {
        "temperature": 0.5,
        "max_tokens": 100
    }
    llm = AbstractLLM(config)
    assert llm.config == config
    assert llm.prompt is None
    assert llm.session_id is None
    assert llm.relevant_contents is None
    assert llm.dataset is None
    assert llm.llm_api_key is None
    assert llm.parent_session_id is None
    with pytest.raises(NotImplementedError):
        llm.memory

    with pytest.raises(NotImplementedError):
        llm.llm

    assert llm.preprocess("input") == "input"
    assert llm.generate_prompt("text") == "text"

def test_get_llm_class_get_default_class():
    llm_class = get_llm_class()
    assert llm_class == DialogLLM

def test_get_llm_class_get_custom_class():
    os.environ["LLM_CLASS"] = "dialog_lib.agents.abstract.AbstractLLM"
    llm_class = get_llm_class()
    assert llm_class == AbstractLLM

def test_get_llm_class_with_invalid_class():
    os.environ["LLM_CLASS"] = "dialog.llm.invalid_llm.InvalidLLM"
    with pytest.raises(ModuleNotFoundError):
        llm_class = get_llm_class()