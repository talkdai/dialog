from pathlib import Path

import tomllib
from decouple import config

LOGGING_LEVEL = config("LOGGING_LEVEL", default="INFO")

DATABASE_URL = config("DATABASE_URL")
OPENAI_API_KEY = config("OPENAI_API_KEY")
VERBOSE_LLM = config("VERBOSE_LLM", default=False, cast=bool)
PROJECT_CONFIG = config(
    "PROJECT_CONFIG",
    cast=lambda filename: tomllib.loads(Path(filename).read_text()),
    default={},
)

DEFAULT_LLM_CONFIG = {"temperature": 0.2, "model_name": "gpt-3.5-turbo"}
LLM_CONFIG = {**DEFAULT_LLM_CONFIG, **PROJECT_CONFIG.get("llm", {})}
MODEL_NAME = LLM_CONFIG.get("model_name", "gpt-3.5-turbo")

PROMPT = PROJECT_CONFIG.get("prompt", {})
