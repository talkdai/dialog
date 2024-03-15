import pytest

from dialog.llm.abstract_llm import AbstractLLM


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
    assert llm.llm_key is None
    assert llm.parent_session_id is None
    with pytest.raises(NotImplementedError):
        llm.memory

    with pytest.raises(NotImplementedError):
        llm.llm

    assert llm.preprocess("input") == "input"
    assert llm.generate_prompt("text") == "text"

    with pytest.raises(NotImplementedError):
        llm.get_prompt("input")