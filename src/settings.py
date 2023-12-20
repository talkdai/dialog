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
PLUGINS = config("PLUGINS", cast=lambda s: s.split(","), default="")

# Used to load custom LLM classes
LLM_CLASS = config("LLM_CLASS", default=None)

WHATSAPP_VERIFY_TOKEN = config("WHATSAPP_VERIFY_TOKEN", "1234567890")
WHATSAPP_API_TOKEN = config("WHATSAPP_API_TOKEN", "1234567890")
WHATSAPP_ACCOUNT_NUMBER = config("WHATSAPP_ACCOUNT_NUMBER", "")