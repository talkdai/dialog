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
LLM_CONFIG = PROJECT_CONFIG.get("llm") or {"temperature": 0.2}

PROMPT = PROJECT_CONFIG.get("prompt", {})
MODEL_NAME = PROMPT.get("model_name", "gpt-3.5-turbo")
WHATSAPP_VERIFY_TOKEN = config("WHATSAPP_VERIFY_TOKEN", "1234567890")
WHATSAPP_API_TOKEN = config("WHATSAPP_API_TOKEN", "1234567890")