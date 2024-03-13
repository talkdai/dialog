import tomllib
from pathlib import Path

from decouple import Csv, Config

config = Config(".env")

LOGGING_LEVEL = config.get("LOGGING_LEVEL", default="INFO")

DATABASE_URL = config.get("DATABASE_URL")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")
VERBOSE_LLM = config.get("VERBOSE_LLM", default=False, cast=bool)
PLUGINS = config.get("PLUGINS", cast=Csv(), default=None)

# Project (`.toml`) configuration
PROJECT_CONFIG = config.get(
    "PROJECT_CONFIG",
    cast=lambda filename: tomllib.loads(Path(filename).read_text()),
    default={},
)
PROJECT_PROMPT = PROJECT_CONFIG.get("prompt", {})
FALLBACK = PROJECT_PROMPT.get("fallback")
FALLBACK_NOT_FOUND_RELEVANT_CONTENTS = PROJECT_PROMPT.get("fallback_not_found_relevant_contents")

# Langchain and LLM parameters and settings
LLM_CLASS = config.get("LLM_CLASS", default=None)
LLM_TEMPERATURE = config.get("LLM_TEMPERATURE", default=0.2, cast=float)
LLM_RELEVANT_CONTENTS = config.get("LLM_RELEVANT_CONTENTS", default=1, cast=int)
LLM_MEMORY_SIZE = config.get("LLM_MEMORY_SIZE", default=5, cast=int)
STATIC_FILE_LOCATION = config.get("STATIC_FILE_LOCATION", "/app/static")
COSINE_SIMILARITY_THRESHOLD = config.get("COSINE_SIMILARITY_THRESHOLD", default=0.2, cast=float)

# Cors
CORS_ALLOW_ORIGINS = config.get("CORS_ALLOW_ORIGINS", cast=Csv(), default="*")
CORS_ALLOW_CREDENTIALS = config.get("CORS_ALLOW_CREDENTIALS", cast=bool, default=True)
CORS_ALLOW_METHODS = config.get("CORS_ALLOW_METHODS", cast=Csv(), default="*")
CORS_ALLOW_HEADERS = config.get("CORS_ALLOW_HEADERS", cast=Csv(), default="*")
