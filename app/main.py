from contextlib import asynccontextmanager

from decouple import config
from .models.db import session, engine
from .models import Chat, CompanyContent
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from pydantic import BaseModel
from typing import Union, Optional, List, Dict, Any

from .llm import llm
from langchain.schema import HumanMessage

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize csv
    yield
    # exits app


app = FastAPI(
    title="Dialogue API",
    description="Dialogue API for humanized AI",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Chat(BaseModel):
    email: Optional[str]
    name: Optional[str]
    message: str


@app.get("/health")
async def health():
    with engine.connect() as con:
        try:
            con.execute(text('SELECT 1'))
            return {"message": "Dialogue API is healthy"}
        except:
            return {"message": "Failed to execute simple SQL"}


@app.post("/chat")
async def post_message(message: Chat):
    # Save message to db
    # Process message with langchain and
    return {"message": llm.invoke(message.message)}


@app.get("/chat")
async def get_chat_content():
    return {"message": "First FastAPI app"}


@app.post("/session")
async def create_session():
    return {"message": "First FastAPI app"}
