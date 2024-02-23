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
LLM_TEMPERATURE = config("LLM_TEMPERATURE", default=0.2, cast=float)
LLM_RELEVANT_CONTENTS = config("LLM_RELEVANT_CONTENTS", default=1, cast=int)
LLM_MEMORY_SIZE = config("LLM_MEMORY_SIZE", default=5, cast=int)
STATIC_FILE_LOCATION = config("STATIC_FILE_LOCATION", "/app/static")
CONSINE_SIMILARITY_THRESHOLD = config("CONSINE_SIMILARITY_THRESHOLD", default=0.2, cast=float)

# Cors
CORS_ALLOW_ORIGINS = config("CORS_ALLOW_ORIGINS", cast=Csv(), default="*")
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", cast=bool, default=True)
CORS_ALLOW_METHODS = config("CORS_ALLOW_METHODS", cast=Csv(), default="*")
CORS_ALLOW_HEADERS = config("CORS_ALLOW_HEADERS", cast=Csv(), default="*")
