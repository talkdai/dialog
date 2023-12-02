import logging

from typing import Any
from webhooks.responses import *
from urllib.parse import urlparse

from fastapi import APIRouter, Request, Body
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

POSSIBLE_ORIGINS = {
    "facebook": whatsapp_serializer,
}

GET_RESPONSES = {
    "facebook": whatsapp_get_response,
}

POST_RESPONSES = {
    "facebook": whatsapp_post_response
}

@router.get("/{origin}")
def webhook_get(origin: str, request: Request):
    is_existing_origin = origin in POSSIBLE_ORIGINS.keys()
    if not is_existing_origin:
        raise HTTPException(status_code=404)

    response_function = GET_RESPONSES.get(origin, None)

    return response_function(request)


@router.post("/{origin}")
def webhook_post(origin: str, request: Request, payload: Any = Body(None)):
    serializer = POST_RESPONSES.get(origin, None)
    if serializer is None:
        raise HTTPException(status_code=404)

    return serializer(request, payload)