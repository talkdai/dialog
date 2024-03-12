import tomllib
from pathlib import Path

from decouple import Csv, config

LOGGING_LEVEL = config("LOGGING_LEVEL", default="INFO")

DATABASE_URL = config("DATABASE_URL")
OPENAI_API_KEY = config("OPENAI_API_KEY")
VERBOSE_LLM = config("VERBOSE_LLM", default=False, cast=bool)
PLUGINS = config("PLUGINS", cast=Csv(), default=None)

# Project (`.toml`) configuration
PROJECT_CONFIG = config(
    "PROJECT_CONFIG",
    cast=lambda filename: tomllib.loads(Path(filename).read_text()),
    default={},
)
PROJECT_PROMPT = PROJECT_CONFIG.get("prompt", {})
FALLBACK = PROJECT_PROMPT.get("fallback")
FALLBACK_NOT_FOUND_RELEVANT_CONTENTS = PROJECT_PROMPT.get("fallback_not_found_relevant_contents")

# Langchain and LLM parameters and settings
LLM_CLASS = config("LLM_CLASS", default=None)
LLM_TEMPERATURE = config("LLM_TEMPERATURE", default=0.2, cast=float)
LLM_RELEVANT_CONTENTS = config("LLM_RELEVANT_CONTENTS", default=1, cast=int)
LLM_MEMORY_SIZE = config("LLM_MEMORY_SIZE", default=5, cast=int)
STATIC_FILE_LOCATION = config("STATIC_FILE_LOCATION", "/app/static")
COSINE_SIMILARITY_THRESHOLD = config("CONSINE_SIMILARITY_THRESHOLD", default=0.2, cast=float)

# knowledge base
EMBED_COLUMNS = config("EMBED_COLUMNS", cast=Csv(), default=["content"])

# Cors
CORS_ALLOW_ORIGINS = config("CORS_ALLOW_ORIGINS", cast=Csv(), default="*")
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", cast=bool, default=True)
CORS_ALLOW_METHODS = config("CORS_ALLOW_METHODS", cast=Csv(), default="*")
CORS_ALLOW_HEADERS = config("CORS_ALLOW_HEADERS", cast=Csv(), default="*")
