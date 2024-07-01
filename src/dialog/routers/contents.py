# *-* coding: utf-8 *-*
from uuid import uuid4
import datetime
import logging

from dialog.db import engine, get_session
from dialog_lib.db.models import CompanyContent
from dialog.schemas import (
    ContentModel
)

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from dialog.settings import Settings

contents_router = APIRouter()

@contents_router.get("/")
async def get_all_contents(session: Session = Depends(get_session)):
    """
    Returns the model that is available inside Dialog in the OpenAI format.
    """
    contents_q = session.query(CompanyContent).all()
    contents = []
    for content in contents_q:
        contents.append(ContentModel(
            question=content.question,
            content=content.content
        ))

    return contents
