# *-* coding: utf-8 *-*
import logging

from importlib_metadata import entry_points

from dialog.settings import Settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dialog.routers import api_router, open_ai_api_router

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

    app.include_router(
        api_router, prefix="",
    )

    app.include_router(
        open_ai_api_router, prefix="/openai"
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

    return app


app = get_application()