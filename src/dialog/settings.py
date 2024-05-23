import tomllib
from pathlib import Path

from decouple import Csv, Config

config = Config(".env")

class Settings:

    @property
    def LOGGING_LEVEL(self):
        return config.get("LOGGING_LEVEL", default="INFO")

    @property
    def DATABASE_URL(self):
        return config.get("DATABASE_URL")

    @property
    def STATIC_FILE_LOCATION(self):
        return config.get("STATIC_FILE_LOCATION", "/app/static")

    @property
    def OPENAI_API_KEY(self):
        return config.get("OPENAI_API_KEY")

    @property
    def VERBOSE_LLM(self):
        return config.get("VERBOSE_LLM", default=False, cast=bool)

    @property
    def PLUGINS(self):
        return config.get("PLUGINS", cast=Csv(), default=None)

    # Project (`.toml`) configuration

    @property
    def PROJECT_CONFIG(self):
        return config.get(
            "PROJECT_CONFIG",
            cast=lambda filename: tomllib.loads(Path(filename).read_text()),
            default={},
        )

    @property
    def PROJECT_PROMPT(self):
        return self.CONFIG.get("prompt", {})

    @property
    def FALLBACK(self):
        return self.PROJECT_PROMPT.get("fallback")

    @property
    def FALLBACK_NOT_FOUND_RELEVANT_CONTENTS(self):
        return self.PROJECT_PROMPT.get("fallback_not_found_relevant_contents")

    # Langchain and LLM parameters and settings

    @property
    def LLM_CLASS(self):
        return config.get("LLM_CLASS", default=None)

    @property
    def LLM_TEMPERATURE(self):
        return config.get("LLM_TEMPERATURE", default=0.2, cast=float)

    @property
    def LLM_RELEVANT_CONTENTS(self):
        return config.get("LLM_RELEVANT_CONTENTS", default=1, cast=int)

    @property
    def LLM_MEMORY_SIZE(self):
        return config.get("LLM_MEMORY_SIZE", default=5, cast=int)

    @property
    def COSINE_SIMILARITY_THRESHOLD(self):
        return config.get("COSINE_SIMILARITY_THRESHOLD", default=0.5, cast=float)

    # Cors
    @property
    def CORS_ALLOW_ORIGINS(self):
        return config.get("CORS_ALLOW_ORIGINS", cast=Csv(), default="*")

    @property
    def CORS_ALLOW_CREDENTIALS(self):
        return config.get("CORS_ALLOW_CREDENTIALS", cast=bool, default=True)

    @property
    def CORS_ALLOW_METHODS(self):
        return config.get("CORS_ALLOW_METHODS", cast=Csv(), default="*")

    @property
    def CORS_ALLOW_HEADERS(self):
        return config.get("CORS_ALLOW_HEADERS", cast=Csv(), default="*")