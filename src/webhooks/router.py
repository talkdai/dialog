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
    "facebookplatform/1.0 (+http://developers.facebook.com)": whatsapp_serializer,
    "facebookexternalua": whatsapp_serializer
}

POSSIBLE_RESPONSES = {
    "facebookplatform/1.0 (+http://developers.facebook.com)": whatsapp_get_response,
    "facebookexternalua": whatsapp_post_response
}

def detect_origin(request):
    """
    Detects the request origin, so we can specify which serializer to use
    """
    referer = request.headers.get('referer')
    origin = request.headers.get('origin')
    user_agent = request.headers.get('user-agent')
    if referer or origin:
        referer = urlparse(referer).netloc
        origin = urlparse(origin).netloc
    else:
        referer = None
        origin = None
    return referer, origin, user_agent


@router.get("/")
def webhook_get(request: Request):
    referer_header, origin_header, user_agent_header = detect_origin(request)
    origin = referer_header or origin_header or user_agent_header
    is_existing_origin = origin in POSSIBLE_ORIGINS.keys()
    if not is_existing_origin:
        raise HTTPException(status_code=404)

    response_function = POSSIBLE_RESPONSES.get(origin, None)

    return response_function(request)


@router.post("/")
def webhook_post(request: Request, payload: Any = Body(None)):
    referer_header, origin_header, user_agent_header = detect_origin(request)
    origin = referer_header or origin_header or user_agent_header
    serializer = POSSIBLE_RESPONSES.get(origin, None)
    return serializer(request, payload)