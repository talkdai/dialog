# *-* coding: utf-8 *-*
import logging

from importlib_metadata import entry_points

from dialog.settings import Settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dialog.routers import api_router, open_ai_api_router, add_model_router

logging.basicConfig(
    level=Settings().LOGGING_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_application() -> FastAPI:
    app = FastAPI(
        title="Dialog API",
        description="Humanized Conversation API (using LLM)",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=Settings().CORS_ALLOW_ORIGINS,
        allow_credentials=Settings().CORS_ALLOW_CREDENTIALS,
        allow_methods=Settings().CORS_ALLOW_METHODS,
        allow_headers=Settings().CORS_ALLOW_HEADERS,
    )
    from dialog.db import engine, get_session
    from sqlalchemy import text

    @app.get("/health")
    async def health():
        with engine.connect() as con:
            try:
                con.execute(text("SELECT 1"))
                return {"message": "Dialog API is healthy"}
            except:
                return {"message": "Failed to execute simple SQL"}

    app.include_router(
        api_router, prefix="",
    )

    app.include_router(
        open_ai_api_router, prefix="/openai"
    )
    for model in Settings().PROJECT_CONFIG.get("endpoint", []):
    # Think on how to load the models on each of the routers
        add_model_router(
            app,
            model["model_class_path"],
            model.get("path")
        )

    add_model_router(
        app,
        Settings().LLM_CLASS,
        ""
    )

    app.mount("/static", StaticFiles(directory=Settings().STATIC_FILE_LOCATION), name="static")
    plugins = entry_points(group="dialog")
    for plugin in plugins:
        logging.info("Loading plugin: %s", plugin.name)
        try:
            plugin_module = plugin.load()
        except ImportError as e:
            logging.warning(f"Failed to load plugin: {plugin.name}. Traceback: \n\n {e.__str__()}", )
        else:
            try:
                plugin_module.register_plugin(app)
            except AttributeError:
                logging.warning(f"Failed to register plugin: {plugin.name}\n\n{e.__str__()}")

    logging.info("Dialog API started successfully with settings:")

    for setting in dir(Settings):
        if setting.isupper() and setting not in ["LOGGING_LEVEL", "DATABASE_URL", "OPENAI_API_KEY", "PROJECT_CONFIG"]:
            logging.info(f"{setting}: {getattr(Settings(), setting)}")

    return app


app = get_application()