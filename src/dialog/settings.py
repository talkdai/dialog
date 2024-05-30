import tomllib
import logging
from pathlib import Path
from decouple import Csv, Config

config = Config(".env")

logger = logging.getLogger(__name__)

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
        return self.PROJECT_CONFIG.get("prompt", {})

    @property
    def FALLBACK(self):
        return self.PROJECT_PROMPT.get("fallback")

    @property
    def FALLBACK_NOT_FOUND_RELEVANT_CONTENTS(self):
        return self.PROJECT_PROMPT.get("fallback_not_found_relevant_contents")

    # Langchain and LLM parameters and settings

    @property
    def MODEL_SETTINGS(self):
        return self.PROJECT_CONFIG.get("model", {})

    def get_model_setting(self, key, default=None, cast=None, toml_key=None):
        model_setting_value = self.MODEL_SETTINGS.get(key.lower() or toml_key)

        if model_setting_value:
            return model_setting_value

        env_setting_value = config.get(key, default=default, cast=cast)
        message = (
            f"{key} is set in the environment variable setting. "
            "We are deprecating this environment variable and adding it to the model toml file."
        )
        if toml_key:
            message += f"Please add `{toml_key} = {env_setting_value}` to your `[model]` section in the toml."

        logger.warning(message)
        return env_setting_value

    @property
    def LLM_CLASS(self):
        return config.get("LLM_CLASS", default=None)

    @property
    def LLM_TEMPERATURE(self):
        return self.get_model_setting("LLM_TEMPERATURE", default=0.2, cast=float, toml_key="temperature")

    @property
    def LLM_RELEVANT_CONTENTS(self):
        return self.get_model_setting("LLM_RELEVANT_CONTENTS", default=1, cast=int, toml_key="relevant_contents")

    @property
    def LLM_MEMORY_SIZE(self):
        return self.get_model_setting("LLM_MEMORY_SIZE", default=5, cast=int, toml_key="memory_size")

    @property
    def COSINE_SIMILARITY_THRESHOLD(self):
        return self.get_model_setting("COSINE_SIMILARITY_THRESHOLD", default=0.5, cast=float)

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