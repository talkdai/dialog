from pathlib import Path

import tomllib
from decouple import config, Csv

LOGGING_LEVEL = config("LOGGING_LEVEL", default="INFO")

DATABASE_URL = config("DATABASE_URL")
OPENAI_API_KEY = config("OPENAI_API_KEY")
VERBOSE_LLM = config("VERBOSE_LLM", default=False, cast=bool)
PROJECT_CONFIG = config(
    "PROJECT_CONFIG",
    cast=lambda filename: tomllib.loads(Path(filename).read_text()),
    default={},
)
PLUGINS = config("PLUGINS", cast=Csv(), default=None)

# Used to load custom LLM classes
LLM_CLASS = config("LLM_CLASS", default=None)
STATIC_FILE_LOCATION = config("STATIC_FILE_LOCATION", "/app/static")