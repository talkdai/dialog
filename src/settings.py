import tomllib

from decouple import config

DATABASE_URL = config("DATABASE_URL")
OPENAI_API_KEY = config("OPENAI_API_KEY")
VERBOSE_LLM = config("VERBOSE_LLM", default=False, cast=bool)

PROJECT_CONFIG = {}
with open(config("PROJECT_CONFIG"), "rb") as f:
    PROJECT_CONFIG = tomllib.load(f)
